import fetch from 'node-fetch';
import { createClient } from '@supabase/supabase-js';

const rapidapiKey = process.env.RAPIDAPI_KEY;
const supabaseUrl = 'https://ekkdqhznzdyxjgablgfm.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const languages = {
    'python': 92
}

const api = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).end();
    }

    const { code, language , problemNumber } = req.body;

        // get test cases from supabase
        const { data: testCases, error } = await supabase
        .from('test_cases')
        .select('*')
        .eq('problem_number', problemNumber);

    if (error) {
        return res.status(500).json({ error: 'Failed to fetch test cases.' });
    }

    console.log(testCases);

    const results = [];

    const languageId = languages[language];
    if (!languageId) {
        return res.status(400).json({ error: 'Invalid language.' });
    }

    // test for each test case
    for (const testCase of testCases) {
        const input = testCase.input;
        const expectedOutput = testCase.output;

        console.log("checking " + input + "\n expecting " + expectedOutput);
        console.log("code: " + code);
        console.log("\n languageId: " + languageId);

        // submit to judge0
        let submissionToken;
        try {
            const createSubmissionResponse = await fetch('https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&fields=*&wait=true', {
                method: 'POST',
                headers: {
                    'content-type': 'application/json',
                    'Content-Type': 'application/json',
                    'X-RapidAPI-Key': rapidapiKey,
                    'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
                },
                body: JSON.stringify({
                    language_id: languageId,
                    // encode source code to base64
                    source_code: Buffer.from(code).toString('base64'),
                    // encode test input to base64
                    stdin: Buffer.from(input).toString('base64')    
                })
            });
            
            const submissionData = await createSubmissionResponse.json();
            console.log(submissionData);

            // decode submissionData.stdout from base64
            const decodedOutput = Buffer.from(submissionData.stdout, 'base64').toString();

            if (decodedOutput.trim() === expectedOutput.trim()) {
                results.push({ testCaseId: testCase.id, status: 'PASSED' });
            } else {
                results.push({ testCaseId: testCase.id, status: 'FAILED', received: decodedOutput.trim() });
            }

        } catch (error) {
            return res.status(500).json({ error: 'Failed to create submission to Judge0.' });
        }

        // // fetch the result using the Submission Token
        // try {
        //     const resultResponse = await fetch(`https://judge0-ce.p.rapidapi.com/submissions/${submissionToken}?base64_encoded=true`, {
        //         method: 'GET',
        //         headers: {
        //             'X-RapidAPI-Key': rapidapiKey,
        //             'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
        //         }
        //     });

        //     const resultData = await resultResponse.json();
        //     console.log(resultData);

        //     if (resultData.stdout.trim() === expectedOutput.trim()) {
        //         results.push({ testCaseId: testCase.id, status: 'PASSED' });
        //     } else {
        //         results.push({ testCaseId: testCase.id, status: 'FAILED', received: resultData.stdout.trim() });
        //     }

        // } catch (error) {
        //     return res.status(500).json({ error: 'Failed to fetch result from Judge0.' });
        // }
    }
    return res.json({ results });   
};

export default api;
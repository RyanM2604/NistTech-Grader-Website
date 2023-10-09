const fetch = require('node-fetch');
const { createClient } = require('@supabase/supabase-js');

const rapidapiKey = 'RAPIDAPI_KEY';

const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
const supabase = createClient(supabaseUrl, supabaseKey);

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).end();
    }

    const { code, languageId, input, problemNumber } = req.body;

        // get test cases from supabase
        const { data: testCases, error } = await supabase
        .from('test_cases')
        .select('*')
        .eq('problem_number', problemNumber);

    if (error) {
        return res.status(500).json({ error: 'Failed to fetch test cases.' });
    }

    const results = [];

    // test for each test case
    for (const testCase of testCases) {
        const input = testCase.input;
        const expectedOutput = testCase.expected_output;

        // submit to judge0
        let submissionToken;
        try {
            const createSubmissionResponse = await fetch('https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&fields=*', {
                method: 'POST',
                headers: {
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
            submissionToken = submissionData.token;
        } catch (error) {
            return res.status(500).json({ error: 'Failed to create submission.' });
        }

        // fetch the result using the Submission Token
        try {
            const resultResponse = await fetch(`https://judge0-ce.p.rapidapi.com/submissions/${submissionToken}?base64_encoded=true&fields=*`, {
                method: 'GET',
                headers: {
                    'X-RapidAPI-Key': rapidapiKey,
                    'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com'
                }
            });

            const resultData = await resultResponse.json();

            if (resultData.stdout.trim() === expectedOutput.trim()) {
                results.push({ testCaseId: testCase.id, status: 'PASSED' });
            } else {
                results.push({ testCaseId: testCase.id, status: 'FAILED', received: resultData.stdout.trim() });
            }

        } catch (error) {
            return res.status(500).json({ error: 'Failed to fetch result.' });
        }
    }
    return res.json({ results });   
};
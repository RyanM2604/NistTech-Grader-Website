def function():
    inp = input()
    sum = 0
    prev = 0
    mydict = {
        "I" : 1,
        "V" : 5,
        "X" : 10,
        "L" : 50,
        "C" : 100,
        "D" : 500,
        "M" : 1000
    }
    for i in range(len(inp)):
        sum += mydict[inp[i]]
        if mydict[inp[i]] > prev:
            sum = sum - 2*prev
        prev = mydict[inp[i]]
    print(sum)
function()

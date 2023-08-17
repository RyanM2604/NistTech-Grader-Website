def function():
    acheived = int(input())
    total = int(input())
    percent = round((acheived/total * 100), 1)

    if percent >= 82:
        print(7)
    elif percent >= 71 and percent <82:
        print(6)
    elif percent >= 59 and percent <71:
        print(5)
    elif percent >= 47 and percent <59:
        print(4)
    elif percent >= 34 and percent <47:
        print(3)
    elif percent >= 17 and percent <34:
        print(2)
    elif percent >= 9 and percent <17:
        print(1)

function()
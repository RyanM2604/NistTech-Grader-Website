def function():
    str = input()
    
    try: #You need to do try and accept in case there is no input for vowels
        vowels = input()
    except:
        vowels = ''

    vow = []
    final = []
    for i in range(len(vowels)):
        vow.append(vowels[i])
    
    for i in range(0, len(str)):
        if str[i] == "*":
            final.append(vow[0])
            vow.pop(0)
        else:
            final.append(str[i])
    for i in range(len(final)):
        print(final[i], end='')

function()
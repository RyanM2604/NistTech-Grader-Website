def function():
    val = round((int(input())/1023)*5, 2)
    val = "{:.2f}".format(val)
    print(val)
function()
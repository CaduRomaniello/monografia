"""
Get a string in the format hh:mm and converts it to a variable of Time type
"""
function stringToTime(timeString::String)
    
    aux = split(timeString, ':')
    hours = parse(Int, aux[1])
    minutes = parse(Int, aux[2])

    time = DateTime(2022, 1, 1, hours, minutes, 0)
    return Time(time)

end
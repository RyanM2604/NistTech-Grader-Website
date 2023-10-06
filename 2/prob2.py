def convert_temperature(target_scale, temperature_str):
  """Converts a temperature from one scale to another.

  Args:
    target_scale: The target temperature scale.
    temperature_str: A string representing the temperature to be converted.

  Returns:
    A float representing the converted temperature.
  """

  # Check if the target scale is valid.
  if target_scale not in ["Celsius", "Fahrenheit", "Kelvin"]:
    raise ValueError("Invalid target scale: {}".format(target_scale))

  # Get the temperature value and the unit.
  temperature_value = float(temperature_str[:-1])
  unit = temperature_str[-1]

  # Convert the temperature to the target scale.
  if target_scale == "Celsius":
    if unit == "F":
      temperature_value = (temperature_value - 32) * 5 / 9
    elif unit == "K":
      temperature_value = temperature_value - 273.15
  elif target_scale == "Fahrenheit":
    if unit == "C":
      temperature_value = temperature_value * 9 / 5 + 32
    elif unit == "K":
      temperature_value = (temperature_value - 273.15) * 9 / 5 + 32
  elif target_scale == "Kelvin":
    if unit == "C":
      temperature_value = temperature_value + 273.15
    elif unit == "F":
      temperature_value = (temperature_value - 32) * 5 / 9 + 273.15

  # Return the converted temperature.
  return round(temperature_value, 2)

# Example usage:



converted_temperature = convert_temperature(input(), input())

print(converted_temperature)

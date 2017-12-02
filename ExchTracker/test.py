import numpy
import talib
import pendulum


now=pendulum.now()
pendulum.set_formatter('alternative')
OutputFile="CndleRun-" + now.format('YYYY-MM-DD-HHmmss') + ".csv"
print(OutputFile)
quit()

close = numpy.random.random(30)
print(close)
output = talib.SMA(close,timeperiod=12)
print(output)
output = talib.EMA(close,timeperiod=12)
print(output)

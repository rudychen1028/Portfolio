#! /usr/bin/python

#import modules
import sys, psutil, getopt

#nagios return codes
UNKNOWN = -1
OK = 0
WARNING = 1
CRITICAL = 2
usage = 'usage: ./check_cpu.py -w/--warn <integer> -c/--crit <integer>'

# get overall cpu use
def total_cpu():
  total_cpu_use = psutil.cpu_percent(interval=1, percpu=False)
  return total_cpu_use

# get per core cpu use
def percore_cpu():
  percore_cpu_use = []
  cpu_id = 0
  for cpu in psutil.cpu_percent(interval=1, percpu=True):
    array_line = str(cpu_id), cpu
    percore_cpu_use.append(array_line)
    cpu_id += 1
  return percore_cpu_use

#Nagios performance data
def performance_data(total_cpu_use, percore_cpu_use, warn, crit):
  percore_data = ()
  for percore_cpu in percore_cpu_use:
    percore_data += str('CPU-') + str(percore_cpu[0]), '=', str(percore_cpu[1]), str('%;'), str('99'), ';', str(''), ';', str('0'), ';', str('')
  percore_cpu_data = "".join(percore_data)
#  print percore_cpu_data
  total_data = str('Total'), '=',  str(total_cpu_use), str('%;'), str(warn), ';', str(crit), ';', str('0'), ';', str('100')
  total_cpu_data = "".join(total_data)
#  print total_cpu_data
  performance_data =  total_cpu_data + percore_cpu_data
  return performance_data

#check total CPU 
def total_cpu_check(total_cpu_use, percore_cpu_use, warn, crit, perf_data):
  result = None
  if total_cpu_use > crit:
    print ('CRITICAL - Total CPU use is', total_cpu_use, '% |', perf_data)
    result = 1
    sys.exit(CRITICAL)
  elif total_cpu_use > warn:
    print ('WARNING - Total CPU use is', total_cpu_use, '% |', perf_data)
    result = 1
    sys.exit(WARNING)
  else:
    for core in percore_cpu_use:
      if core[1] > 99:
        print ('WARNING - CPU Core', core[0], 'is at', core[1], '% |', perf_data)
        result = 1
        sys.exit(WARNING)
      else:
        continue
  return result
# define command lnie options and validate data.  Show usage or provide info on required options
def command_line_validate(argv):
  try:
    opts, args = getopt.getopt(argv, 'w:c:o:', ['warn=' ,'crit='])
  except getopt.GetoptError:
    print (usage)
  try:
    for opt, arg in opts:
      if opt in ('-w', '--warn'):
        try:
          warn = int(arg)
        except:
          print ('***warn value must be an integer***')
          sys.exit(CRITICAL)
      elif opt in ('-c', '--crit'):
        try:
          crit = int(arg)
        except:
          print ('***crit value must be an integer***')
          sys.exit(CRITICAL)
      else:
        print (usage)
    try:
      isinstance(warn, int)
      #print 'warn level:', warn
    except:
      print ('***warn level is required***')
      print (usage)
      sys.exit(CRITICAL)
    try:
      isinstance(crit, int)
      #print 'crit level:', crit
    except:
      print ('***crit level is required***')
      print (usage)
      sys.exit(CRITICAL)
  except:
    sys.exit(CRITICAL)
  # confirm that warning level is less than critical level, alert and exit if check fails
  if warn > crit:
    print ('***warning level must be less than critical level***')
    sys.exit(CRITICAL)
  return warn, crit

# main function
def main():
  argv = sys.argv[1:]
  warn, crit = command_line_validate(argv)
  total_cpu_use = total_cpu()
#  print total_cpu_use
  percore_cpu_use = percore_cpu()
#  print percore_cpu_use
  perf_data = performance_data(total_cpu_use, percore_cpu_use, warn, crit)
#  print perf_data
  result = total_cpu_check(total_cpu_use, percore_cpu_use, warn, crit, perf_data)
  if result == None:
    print ('OK - ', total_cpu_use, '% |', perf_data)

if __name__ == '__main__':
  main()

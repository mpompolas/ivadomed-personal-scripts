import sys

# This flushes everything that is printed to a log file

log_file = '/home/nas/PycharmProjects/ivadomed-personal-scripts/logtodelete.log'

old_stdout = sys.stdout
batch_log = open(log_file, 'w')
sys.stdout = batch_log

print('first thing here', file=batch_log, flush=True)
print('this is included too')

sys.stdout = old_stdout

batch_log.close()


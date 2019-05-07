import os
import sys
import logging.handlers

from subprocess import Popen, PIPE

nameserver1 = '8.8.8.8'
nameserver2 = '8.8.4.4'

def main():
   filepath = sys.argv[1]

   if not os.path.isfile(filepath):
       logger.debug("File path {} does not exist. Exiting...".format(filepath))
       sys.exit()

   hosts = {}

   with open(filepath) as fp:
       cnt = 0
       for line in fp:
           logger.debug("line {} contents {}".format(cnt, line))
           record_word_cnt(line.strip().split(' '), hosts)
           cnt += 1

   resolve = use_nslookup(hosts, nameserver1)
   resolve = use_nslookup(hosts, nameserver2)

def use_nslookup(hosts, nameserver):
   p = {} # ip -> process
   p['flush'] = Popen(['sudo', 'service', 'nscd', 'restart'], stdout=PIPE) # clear cache on Linux
   # p['flush'] = Popen(['sudo', 'killall', '-HUP', 'mDNSResponder'], stdout=PIPE) # clear cache on Mac
   flush = p['flush'].communicate()
   logger.debug(flush)
   for n in hosts: # start ping processes
      ip = "%s.floordecor.com" % n
      p[ip] = Popen(['nslookup', ip, nameserver], stdout=PIPE)
      lookup = p[ip].communicate()
      logger.info(lookup)
      #NOTE: you could set stderr=subprocess.STDOUT to ignore stderr also

   while p:
      for ip, proc in p.items():
          if proc.poll() is not None: # ping finished
              del p[ip] # remove from the process list
              if proc.returncode == 0:
                  logger.debug('%s active' % ip)
              elif proc.returncode == 1:
                  logger.warning('%s no response' % ip)
              else:
                  logger.error('%s error' % ip)
              break

def record_word_cnt(words, hosts):
   for word in words:
       if word != '':
           if word.lower() in hosts:
               hosts[word.lower()] += 1
           else:
               hosts[word.lower()] = 1

if __name__ == '__main__':
   logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
   logger = logging.getLogger('resolve-a-list')
   logfile = logging.handlers.RotatingFileHandler('test.log', maxBytes=1000000, backupCount=5)
   logger.addHandler(logfile)
   main()

import os
import sys
import subprocess

# constants
filename = "__finalfile__"
stdfilename = "__stdfilename__"
output_location = "__outputlocation__"
redirector = "__redirector__"
copy_command = "__copycommand__"

if sys.argv[2] == 'atto':
  tag_info_frontend = subprocess.check_output("git -C CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/ describe --tags --long", shell=True)
if sys.argv[2] == 'histo':
  tag_info_frontend = subprocess.check_output("git -C CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_histo/ describe --tags --long", shell=True)
tag_info_frontend = tag_info_frontend.split('-')
f_tag = tag_info_frontend[0].replace('.','p')
f_commits = tag_info_frontend[1]
if f_commits == '0': f_commits = ''
else: f_commits = 'c'+f_commits

if __name__ == "__main__":
  full_command = copy_command + " " + filename + " " + redirector + output_location + "/" + filename.replace('.root',''+f_tag+f_commits+'_'+str(sys.argv[1])+'.root')
  print "Stageout: command:", full_command
  stat = int(os.system(full_command))
  if not stat == 0:
    print "Stageout: FAILURE with exit code", stat
    raise SystemExit(1)

  #full_command = copy_command + " " + stdfilename + " " + redirector + output_location + "/" + stdfilename.replace('.txt', '')+'_'+str(sys.argv[1])+".txt"
  #print "Stageout: command:", full_command
  #stat = int(os.system(full_command))
  #if not stat == 0:
  #  print "Stageout: FAILURE with exit code", stat
  #  raise SystemExit(1)

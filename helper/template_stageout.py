import os
import sys

# constants
filename = "__finalfile__"
stdfilename = "__stdfilename__"
output_location = "__outputlocation__"
redirector = "__redirector__"
copy_command = "__copycommand__"

if __name__ == "__main__":
  full_command = copy_command + " " + filename + " " + redirector + output_location + "/" + filename.replace('.root', '')+'_'+str(sys.argv[1])+".root"
  print "Stageout: command:", full_command
  stat = int(os.system(full_command))
  if not stat == 0:
    print "Stageout: FAILURE with exit code", stat
    raise SystemExit(1)
  #full_command = copy_command + " " + stdfilename + " " + redirector + output_location + "/" + stdfilename.replace('.txt', '')+'_'+str(sys.argv[1])+".txt"
  print "Stageout: command:", full_command
  stat = int(os.system(full_command))
  if not stat == 0:
    print "Stageout: FAILURE with exit code", stat
    raise SystemExit(1)

# Test if the specimen's error log is empty.

logfile=models/genome0/err.txt
if test `wc -l < $logfile` -gt 0
then
	if test `grep --invert-match Warning $logfile | wc -l` -gt 0
	then
		echo "$logfile not empty, has only warnings though."
		exit 0
	else
		# Return a non-reserved exit code, see
		# http://tldp.org/LDP/abs/html/exitcodes.html
		echo "$logfile not empty! Showing its 10 first lines."
		head $logfile
		exit 70 # "internal software error"
	fi
fi

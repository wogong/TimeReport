LASTDAY = $(shell date --date="yesterday" +"%Y%m%d")
LASTDAY_FILE = "./img/$(LASTDAY).png"
LASTWEEK = $(shell date --date="-7 days" +"%YW%V")
LASTWEEK_FILE = "./img/$(LASTWEEK).png"
LASTMONTH = $(shell date --date="-30 days" +"%YM%m")
LASTMONTH_FILE = "./img/$(LASTMONTH).png"

day:
	python3 ~/Dropbox/Server/TimeReport/main.py --report --level 0 --time $(LASTDAY)
	coscmd upload $(LASTDAY_FILE) imgs/time/

week:
	python3 ~/Dropbox/Server/TimeReport/main.py --report --level 1 --time $(LASTWEEK)
	coscmd upload $(LASTWEEK_FILE) imgs/time/

month:
	python3 ~/Dropbox/Server/TimeReport/main.py --report --level 2 --time $(LASTMONTH)
	coscmd upload $(LASTMONTH_FILE) imgs/time/
import sys
from datetime import datetime

DEBUG_MODE = 0

def dprint( string ):
    if DEBUG_MODE:
        print( string )

def main():
    if len(sys.argv) <= 1 :
        print("Syntax Error: %s <inputfile>" % sys.argv[0])
        return
    current_day = ""
    current_date = ""
    current_day_total = 0
    #gallons per minute based on pump specs
    #currently using Hydromatic (SHEF40) submersible effluent pump
    #pushing ~21 feet or pipe with 10 feet of elivation (head) 
    #Translation: flow rate of ~7.5 US gallons per minute based on datasheet
    flowrate = 7.5
    g_to_cm = 0.00378541
    g_to_l = 3.78541
    volume = 0
    #because gravity empties pipe after it shuts off we need to subtract the volume
    #of fluid in the pipe after each time it gets turned on.  20' @1.5" = ~2 US gallons
    #...or... cause we measured the time it takes for fluid to reach the tipping chambers
    #... -7 seconds
    delay = 7   # 7 seconds based on delay pushing effluent uphill... 

    print("Date, Day, Pump on-time, Seconds, US Gallons, Liters")
    with open(sys.argv[1]) as infile:
        for line in infile :
            if line.startswith('202') :
                line = line.replace(',', '')
                date1, day1, time1, static1, state1 = line.strip().split()
                if state1 != "ON":
                    dprint("expected ON state, going to next line\n")
                    continue
                t1 = datetime.strptime("%s %s" % (date1, time1), "%Y-%m-%d %H:%M:%S")
                #are we calculating on-time for a new day?
                if current_date != "" and current_date != date1 :
                    volume = current_day_total * (flowrate/60)
                    print("%s, %s, Pump on-time, %d, %.1f, %.1f" % \
                            (current_date, current_day, current_day_total, volume, volume*g_to_l))
                    current_day_total = 0

                #TODO: figure out date roll-over...

                #are we calculating on-tie for the first time or a change of date?
                #then set up a current values
                if current_date == 0 or current_date != date1 :
                    current_day = day1
                    current_date = date1
                    current_day_total = 0
    
                try: 
                    line = next(infile)
                except:
                    dprint("Missing next line: expected OFF State\n")
                    continue
                line = line.replace(',', '')
                date2, day2, time2, static2, state2 = line.strip().split()
                #if working properly, ON should be followed by an OFF
                if state2 != "OFF":
                    dprint("expected OFF state, going to next line\n")
                    continue
                t2 = datetime.strptime("%s %s" % (date2, time2), "%Y-%m-%d %H:%M:%S")
                elapsed = t2 - t1
                current_day_total += elapsed.total_seconds() - delay #cause we only poll every other second.
                #...and we could be off by as much as ~2 seconds.
                dprint(current_day_total)
            else:
                dprint(line)
    if current_day_total != 0 :
        volume = current_day_total * (flowrate/60)
        print("%s, %s, Pump on-time, %d, %.1f, %.1f" % \
               (current_date, current_day, current_day_total, volume, volume*g_to_l))
    else :
        date = sys.argv[1].split('.')[1]
        day = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
        print("%s, %s, Pump on-time, 0, 0, 0" % (date,day))

if __name__ == "__main__":
  main()



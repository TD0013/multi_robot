# Task message type/class
# Time is in seconds after initialization of WS
int32 taskID #unique id

int64 arrivalTime
int64 startTime #to be done any time after this
int64 finishTime #to be done any time before this

string pickup #start position
string destination #end position

int64 demand    # demand

int32 type #depends on robot
int32 timeconstraint #0 for soft, 1 for hard

int32 softPenalty = 10 #perSecond
int32 hardPenalty = 1000000
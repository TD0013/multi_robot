# Time is in seconds after initialization of WS
int32 taskID

int64 arrivalTime
int64 startTime # any time after this
int64 finishTime # any time before this

string pickup
string destination

int64 demand

int32 type #depends on robot
int32 timeconstraint #0 for soft, 1 for hard

int32 softPenalty = 10 #perSecond
int32 hardPenalty = 1000000
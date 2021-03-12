#!../../bin/linux-arm/mcc118

## You may have to change mcc118 to something else
## everywhere it appears in this file

< envPaths
epicsEnvSet("PVPREFIX","MCC")

cd "${TOP}"

## Register all support components
dbLoadDatabase "dbd/mcc118.dbd"
mcc118_registerRecordDeviceDriver pdbbase

## Load record instances
#dbLoadTemplate "db/user.substitutions"
#dbLoadTemplate "db/mccVersion.db", "user=pi"

dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=0,SCAN=1 second")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=1")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=2")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=3")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=4")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=5")
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=6") #not defined
#dbLoadRecords("db/mcc118.db","PVPREFIX=${PVPREFIX}, HA=0, CH=7") #not defined

dbLoadRecords("db/channelmapping.db", "P=FHIFEL, R=LLRFSRC")

cd "${TOP}/iocBoot/${IOC}"
iocInit

## Start any sequence programs
#seq sncxxx,"user=pi"

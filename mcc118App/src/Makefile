TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = mcc118
# mcc118.dbd will be created and installed
DBD += mcc118.dbd

# mcc118.dbd will be made up from these files:
mcc118_DBD += base.dbd

# Include dbd files from all support applications:
mcc118_DBD += mcc118dev.dbd

# Add all the support libraries needed by this IOC
USR_SYS_LIBS += daqhats

# mcc118_registerRecordDeviceDriver.cpp derives from mcc118.dbd
mcc118_SRCS += mcc118_registerRecordDeviceDriver.cpp
mcc118_SRCS += devMcc118.c

# Build the main IOC entry point on workstation OSs.
mcc118_SRCS_DEFAULT += mcc118Main.cpp

# Add support from base/src/vxWorks if needed
#mcc118_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
mcc118_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <dbScan.h>
#include <dbAccess.h>
#include <devSup.h>
#include <recGbl.h>
#include <alarm.h>
#include "daqhats_utils.h"

#include <aiRecord.h>

#include <epicsExport.h>

struct mcc118State {
  unsigned int address;
  unsigned int channel;
  uint8_t hat_address;
  IOSCANPVT scan;

  uint32_t user_buffer_size;
  double read_buf[8000]; // 1000 * 8 channels
};

static long init_record(aiRecord *prec)
{
  //printf("begin mcc118 init\n");

  struct mcc118State* priv;
//  char configString = {0};

  priv=malloc(sizeof(struct mcc118State));
  if(!priv){
    recGblRecordError(S_db_noMemory, (void*)prec,
      "devAiMcc118 failed to allocate private struct");
    return S_db_noMemory;
  }

  if (VME_IO != prec->inp.type){
     return(S_dev_badBus);
  }
  priv->address = prec->inp.value.vmeio.card;
  priv->channel = prec->inp.value.vmeio.signal;
  priv->user_buffer_size = 1000 * 8; // always 8 channels

  printf("priv address: %d\n", priv->address);
  printf("priv channel: %d\n", priv->channel);

  priv->hat_address = priv->address; //just copy the address from the record
  printf("priv hat_address: %d\n", priv->hat_address);

  int result;
  uint8_t channel_mask = {CHAN0 | CHAN1 | CHAN2 | CHAN3 | CHAN4 | CHAN5 | CHAN6 | CHAN7}; //since there can only be one connection to the HAT, always read all channels
  uint32_t options = OPTS_CONTINUOUS;
  uint32_t samples_per_channel = 0; //continous scan ignores this it just needs to be set
  double scan_rate = 1000.0;

  // Open a connection to the device, only if its not already open
  if(mcc118_is_open(priv->hat_address) == 0){ 
    result = mcc118_open(priv->hat_address);
    STOP_ON_ERROR(result);
    result = mcc118_a_in_scan_start(priv->hat_address, channel_mask, samples_per_channel,
          scan_rate, options);
    STOP_ON_ERROR(result);
  };

  prec->dpvt=priv;
  return 0;

  //handler for STOP_ON_ERROR
  stop:
    print_error(mcc118_a_in_scan_stop(priv->hat_address));
    print_error(mcc118_a_in_scan_cleanup(priv->hat_address));
    print_error(mcc118_close(priv->hat_address));

    return 0;
}

static long read_ai(aiRecord *prec)
{
  //printf("read ai start!\n");
  struct mcc118State* priv=prec->dpvt;
  if(!priv) {
    (void)recGblSetSevr(prec, COMM_ALARM, INVALID_ALARM);
    return 0;
  }
  //printf("read ai!\n");

  double value = 0.0;
  int result;
  uint16_t read_status = 0;
  uint32_t samples_read_per_channel = 0;
  int32_t read_request_size = READ_ALL_AVAILABLE;
  double timeout = 5.0;


  //actually read data from the device, all available points
  usleep(50000); //sleep a bit so more samples can accumulate // TODO BAD HACK IDK?
  result = mcc118_a_in_scan_read(priv->hat_address, &read_status, read_request_size,
        timeout, priv->read_buf, priv->user_buffer_size, &samples_read_per_channel);       
  //printf("issued read command for HA%d CH%d\n", priv->hat_address, priv->channel);
  STOP_ON_ERROR(result);

  if (read_status & STATUS_HW_OVERRUN){
      printf("Hardware overrun\n");
  }else if (read_status & STATUS_BUFFER_OVERRUN){
      printf("Buffer overrun\n");
  }

  //printf("samples_read_per_channel: %d\n", samples_read_per_channel);
  if (samples_read_per_channel > 0)
  {
    //printf("read values. HA%d CH%d: ", priv->hat_address, priv->channel);
    int index = samples_read_per_channel * 8 - 8; // 8 channels
    value = priv->read_buf[index + priv->channel]; //only get the data for the records' channel
    //printf("%f\n", value);
    prec->val = floorf(value * 100) / 100;
  }

  return 2; //correct return value is 2. zero does not process the record

  //handler for STOP_ON_ERROR
  stop:
    print_error(mcc118_a_in_scan_stop(priv->hat_address));
    print_error(mcc118_a_in_scan_cleanup(priv->hat_address));
    print_error(mcc118_close(priv->hat_address));

    return 0;
}

static long get_ioint_info(int dir,dbCommon*prec,IOSCANPVT*io)
{
  //printf("get_ioint_info starts\n");
  struct mcc118State* priv=prec->dpvt;
  //printf("get_ioint_info after dpvt assignment\n");
  if(priv) {
    *io = priv->scan;
  }
  //printf("get_ioint_info after putting back IOSCANPVT\n");
  return 0;
}

struct {
  long num;
  DEVSUPFUN  report;
  DEVSUPFUN  init;
  DEVSUPFUN  init_record;
  DEVSUPFUN  get_ioint_info;
  DEVSUPFUN  read_ai;
  DEVSUPFUN  special_linconv;
} devMcc118 = {
  6, /* space for 6 functions */
  NULL,
  NULL,
  init_record,
  get_ioint_info,
  read_ai,
  NULL
};
epicsExportAddress(dset,devMcc118);
#ifndef INTERCEPTOR_H
#define INTERCEPTOR_H

extern int init(void *data);
extern int interceptor(void *data, const char *fname, const unsigned long fid);

#endif

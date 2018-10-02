#include <time.h>
#include <stdio.h>
#include <stdlib.h>

void
timeval_subtract (struct timespec *result, struct timespec *x, struct timespec *y)
{
  /* Perform the carry for the later subtraction by updating y. */
  long long nanof = 1 * 1000 * 1000 * 1000; // nano_factor
  
//   if (x->tv_nsec < y->tv_nsec) {
//     int nsec = (y->tv_usec - x->tv_usec) / 1000000 + 1;
//     y->tv_usec -= 1000000 * nsec;
//     y->tv_sec += nsec;
//   }
//   if (x->tv_usec - y->tv_usec > 1000000) {
//     int nsec = (x->tv_usec - y->tv_usec) / 1000000;
//     y->tv_usec += 1000000 * nsec;
//     y->tv_sec -= nsec;
//   }

  result->tv_sec  = x->tv_sec  - y->tv_sec ;
  result->tv_nsec = x->tv_nsec - y->tv_nsec;

    // normalize nanoseconds
    if (result->tv_nsec >= 1 * nanof) {
        result->tv_nsec -= 1 * nanof;
        result->tv_sec  += 1;
    } else 
    if (result->tv_nsec < 0) {
        result->tv_nsec += 1 * nanof;
        result->tv_sec  -= 1;
    }
}

void
print_t(struct timespec *ts) {
        printf("%lld.%.9ld\n", (long long)ts->tv_sec, ts->tv_nsec);
}

int 
main(int argc, char** argv) {
    // parse input

    struct timespec deadline;
    struct timespec after_time;
    struct timespec diff_time;
    // clockid_t cock = CLOCK_PROCESS_CPUTIME_ID;
    // clockid_t cock = CLOCK_MONOTONIC; // does not work, does note relate to `date`
    // clockid_t cock = CLOCK_MONOTONIC_RAW; // does not work
    clockid_t cock = CLOCK_REALTIME; 

    //clock_gettime(cock, &deadline);

    // deadline.tv_nsec = 1000;
    deadline.tv_sec  = (int) strtol(argv[1], NULL, 10); //1;
    deadline.tv_nsec = 0;

    int result = 0;

    result = clock_nanosleep
        ( cock 
        , TIMER_ABSTIME
        , &deadline
        , NULL
        );

    clock_gettime(cock, &after_time);

    print_t(&after_time);
    //timeval_subtract(&diff_time, &after_time, &deadline);


}

/* results

andreas@simcoin:/blockchain/kern/simcoin/code/sys_test$ pexec         --parameters a b c d a1 a2 a3 a4 b1 b2          -e x         -o -         --shell /bin/bash         -- /usr/bin/docker exec parallel_test_2 ./a.out `date -d "+3 seconds" +"%s"`
1532358526.000179639
1532358526.000169236
1532358526.000176139
1532358526.000173446
1532358526.000190836
1532358526.000666067
1532358526.000214696
1532358526.000189326
1532358526.001133356
1532358526.001154039

## updated version with arg parsing clock testing

# CLOCK_REALTIME
kern@x240:~/ak/bac/code/sys_test$ gcc abssleep.c && ./a.out `date -d "+1 seconds" +"%s"`
1532703208.000072248

*/
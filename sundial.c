#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <getopt.h>

#define getTime(x) ((double)(x))

double mod360(double);
double acosD(double);
double asinD(double);
double cosD(double);
double sinD(double);
double goTime(double);
double julianDay(double);
double jstar(double, double);
double computeSolarAngle(double,double,double,int,time_t);
double modD(double,double);
double sunrise(double latitude,double longitude, double tzOffset, time_t relativeTo);
double sunset(double latitude,double longitude, double tzOffset, time_t relativeTo);

double const PI = 3.14159265359;
double const JEPOCH = 2451545.0;
double const UEPOCH = 946728000.0;

double mod360(double x)  {
    return x - 360.0*floor(x/360.0);
}

double acosD(double x) {
    if (x >= 1.0 ) {
        return 0.0;
    }
    if( x <= -1.0) {
        return 180.0;
    }
    return acos(x) * 180.0 / PI;
}

double asinD(double x) {
    return asin(x) * 180.0 / PI;
}

double cosD(double x) {
    return cos(x * PI / 180.0);
}

double sinD(double x) {
    return sin(x * PI / 180.0);
}


double goTime(double x) {
    return UEPOCH + (x-JEPOCH)*86400.0;
}

double julianDay(double x) {
    return (x-UEPOCH)/86400.0 + JEPOCH;
}

double jstar(double longitude, double timet) {
    return 1+floor(julianDay(timet)-0.0009+longitude/360.0+0.5) + 0.0009 - longitude/360;
}

double modD (double a, double b)
{
    if(b < 0) //you can check for b == 0 separately and do what you want
        return modD(a, -b);
    double ret = (double)((int)a % (int)b);
    if(ret < 0)
        ret+=b;
    return ret;
}

double computeSolarAngle(double latitude, double longitude, double OFFSET, int isSunrise, time_t relativeTo) {
    double timet = getTime(relativeTo);
    timet = timet - modD(timet,86400)-OFFSET;
    double ma = mod360(357.5291 + 0.98560028*(jstar(longitude,timet)-JEPOCH));
    double center = 1.9148*sinD(ma) + 0.02*sinD(2.0*ma) + 0.0003*sinD(3.0*ma);
    double el = mod360(ma + 102.9372 + center + 180.0);
    double solarNoon = jstar(longitude,timet) + 0.0053*sinD(ma) - 0.0069*sinD(2.0*el);
    double declination = asinD(sinD(el) * sinD(23.45));
    double hourAngleInDays = acosD((sinD(-0.83)-sinD(latitude)*sinD(declination))/(cosD(latitude)*cosD(declination))) / 360.0;
    if (isSunrise == 1) {
        double sunriseTime = goTime(solarNoon - hourAngleInDays);
        if (sunriseTime < getTime(relativeTo)) {
            sunriseTime = sunriseTime + 24 * 3600;
        }
        return sunriseTime;
    } else {
        return goTime(solarNoon + hourAngleInDays);
    }
}

double sunrise(double latitude, double longitude, double offset, time_t relativeTo)  {
    return computeSolarAngle(latitude,longitude,offset,1,relativeTo);
}

double sunset(double latitude, double longitude, double offset, time_t relativeTo)  {
    return computeSolarAngle(latitude,longitude,offset,0,relativeTo);
}

void
timestamp_to_str(double ts, const char *fmt, char res[32]) {
    struct tm *lt;
    time_t time = (time_t)ts;

    lt = localtime(&time);

    strftime(res, 32, fmt, lt);
}

static inline void
help (void) {
    printf("Usage: sundial --lat={latitude} --lon={longitude} [option]\n\n"
           "-h --help       display this help message\n"
           "-r --sunrise    display time of sunrise\n"
           "-s --sunset     display time of sunset\n"
           "-v --verbose    make text output more human-readable\n"
           "-y --lat        set the latitude for calculation\n"
           "-x --lon        set the longitude for calculation\n\n");
}

int
main(int argc, char *argv[]) {

    static int sunrise_flag;
    static int sunset_flag;
    static int help_flag;
    static int verbose_flag;

    static double lat;
    static double lon;

    int c;
    while (1) {
        static struct option long_options[] = {

            {"sunrise", no_argument, &sunrise_flag, 1},
            {"sunset",  no_argument, &sunset_flag,  1},
            {"help",    no_argument, &help_flag,    1},
            {"verbose", no_argument, &verbose_flag, 1},

            {"lat", required_argument, NULL, 'y'},
            {"lon", required_argument, NULL, 'x'},

            {0,0,0,0},
        };

        int option_index = 0;

        c = getopt_long(argc, argv, "hvrsx:y:", long_options, &option_index);
        
        if (c == -1)
            break;

        switch (c) {
        case 0:
            if (option_index == 3)
                lat = atof(optarg);
            else if (option_index == 4)
                lon = atof(optarg);
            break;
        case 'h':
            help_flag = 1;
            break;
        case 'v':
            verbose_flag = 1;
            break;
        case 'r':
            sunrise_flag = 1;
            break;
        case 's':
            sunset_flag = 1;
            break;
        case 'x':
            lon = atof(optarg);
            break;
        case 'y':
            lat = atof(optarg);
            break;
        case '?':
            break;
        default:
            abort();
        }
    }

    if ((!sunrise_flag && !sunset_flag) || help_flag) {
        help();
        return 0;
    }
    
    time_t t = time(NULL);
    struct tm lt = {0};

    localtime_r(&t, &lt);

    int gmt_offset = (int)(lt.tm_gmtoff/3600);

    double timestamp = getTime(time(NULL));

    char buf[8] = {0};
    if (sunrise_flag) {
        double sunrise_time = sunrise(lat, lon, gmt_offset, timestamp);
        timestamp_to_str(sunrise_time, "%H:%M", buf);
        if (verbose_flag) {
            printf("Time of sunrise [%f %f] (%s): %s\n", lat, lon, lt.tm_zone, buf);
        }
        else {
            printf("%s\n", buf);
        }
    }

    if (sunset_flag) {
        double sunset_time = sunset(lat, lon, gmt_offset, timestamp);
        timestamp_to_str(sunset_time, "%H:%M", buf);
        if (verbose_flag) {
            printf("Time of sunset [%f %f] (%s): %s\n", lat, lon, lt.tm_zone, buf);
        }
        else {
            printf("%s\n", buf);
        }
    }

    return 0;

}

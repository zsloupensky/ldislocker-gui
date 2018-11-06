#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define USER_NAME_MAX_LENGTH 30

int is_valid_name (const char *name)
{
    /*
     * User/group names must match [a-z_][a-z0-9_-]*[$]
     */
    if (('\0' == *name) ||
        !((('a' <= *name) && ('z' >= *name)) || ('_' == *name))) {
        return 0;
    }

    while ('\0' != *++name) {
        if (!(( ('a' <= *name) && ('z' >= *name) ) ||
              ( ('0' <= *name) && ('9' >= *name) ) ||
              ('_' == *name) ||
              ('-' == *name) ||
              ( ('$' == *name) && ('\0' == *(name + 1)) )
             )) {
            return 0;
        }
    }

    return 1;
}

int is_valid_user_name (const char *name)
{
    /*
     * User names are limited by whatever utmp can
     * handle.
     */
    if (strlen (name) > USER_NAME_MAX_LENGTH) {
        return 0;
    }
    if (strlen (name) <= 1) {
        return 1;
    }

    return is_valid_name (name);
}



int main()
{
    char* username = getenv("USER");
    printf("user: %s",username);
    if(is_valid_user_name(username)){
       setuid( 0 );
       system( "/usr/local/bin/ldislocker-gui.py $USER" );
       return 0;
    } 
    else { 
       return 1;
    }
}
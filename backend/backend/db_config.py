#*******************************************************************************#
#****************** DB Configurations *****************************#
#*******************************************************************************#



# Prod DB CONFIG
#*******************************************************************************#

DEFAULT_PROD_DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'OPTIONS': {
         'charset' : 'utf8',
    },
    'NAME': 'nextpulse',
    'USER': 'root',
    'PASSWORD': 'Mbch@He@drn232017Mar',
    'HOST': 'localhost',
}

# Staging DB CONFIG
#*******************************************************************************#

DEFAULT_STAGING_DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'OPTIONS': {
         'charset' : 'utf8',
    },
    'NAME': 'nextpulse_staging',
    'USER': 'root',
    'PASSWORD': 'Mbch@He@drn232017Mar',
    'HOST': 'localhost',
}

# LOCAL DB CONFIG
#*******************************************************************************#

DEFAULT_LOCAL_DATABASE_CONFIG = {
    'ENGINE': 'django.db.backends.mysql',
    'OPTIONS': {
         'charset' : 'utf8',
    },
    'NAME': 'nextpulse',
    'USER': 'root',
    'PASSWORD': 'hdrn59!',
    'HOST': 'localhost',
}

#*******************************************************************************#

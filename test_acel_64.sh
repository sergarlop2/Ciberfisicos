#!/bin/bash

# Broker MQTT y tópico
BROKER="broker.hivemq.com"
PORT=1883
TOPIC="SCF/sejuja/data/aceleracion"

# Mensaje con 64 muestras
MESSAGE='{"l":64,"s":[{"t":"01-01-01T01:01:16.167","a":[177,-74,1022]},{"t":"01-01-01T01:01:16.183","a":[127,-78,1037]},{"t":"01-01-01T01:01:16.203","a":[123,-69,1051]},{"t":"01-01-01T01:01:16.222","a":[88,-67,1010]},{"t":"01-01-01T01:01:16.238","a":[96,-21,1027]},{"t":"01-01-01T01:01:16.257","a":[113,-129,985]},{"t":"01-01-01T01:01:16.277","a":[76,-68,968]},{"t":"01-01-01T01:01:16.292","a":[153,17,1087]},{"t":"01-01-01T01:01:16.312","a":[104,-55,1026]},{"t":"01-01-01T01:01:16.328","a":[110,-43,1044]},{"t":"01-01-01T01:01:16.347","a":[116,-49,1045]},{"t":"01-01-01T01:01:16.367","a":[134,-16,1070]},{"t":"01-01-01T01:01:16.382","a":[109,-46,1037]},{"t":"01-01-01T01:01:16.402","a":[83,-48,1005]},{"t":"01-01-01T01:01:16.421","a":[87,-25,1014]},{"t":"01-01-01T01:01:16.437","a":[95,-18,1025]},{"t":"01-01-01T01:01:16.457","a":[94,-23,1032]},{"t":"01-01-01T01:01:16.476","a":[96,-23,1035]},{"t":"01-01-01T01:01:16.492","a":[96,-22,1033]},{"t":"01-01-01T01:01:16.511","a":[96,-26,1038]},{"t":"01-01-01T01:01:16.531","a":[93,-20,1035]},{"t":"01-01-01T01:01:16.546","a":[91,-23,1034]},{"t":"01-01-01T01:01:16.566","a":[92,-22,1035]},{"t":"01-01-01T01:01:16.582","a":[93,-20,1035]},{"t":"01-01-01T01:01:16.601","a":[95,-21,1034]},{"t":"01-01-01T01:01:16.621","a":[96,-22,1035]},{"t":"01-01-01T01:01:16.636","a":[94,-24,1037]},{"t":"01-01-01T01:01:16.656","a":[93,-23,1038]},{"t":"01-01-01T01:01:16.675","a":[92,-22,1035]},{"t":"01-01-01T01:01:16.691","a":[92,-21,1033]},{"t":"01-01-01T01:01:16.710","a":[94,-21,1033]},{"t":"01-01-01T01:01:16.730","a":[94,-21,1034]},{"t":"01-01-01T01:01:16.746","a":[94,-21,1035]},{"t":"01-01-01T01:01:16.765","a":[93,-21,1033]},{"t":"01-01-01T01:01:16.785","a":[96,-22,1038]},{"t":"01-01-01T01:01:16.800","a":[94,-21,1033]},{"t":"01-01-01T01:01:16.820","a":[94,-21,1036]},{"t":"01-01-01T01:01:16.835","a":[93,-21,1033]},{"t":"01-01-01T01:01:16.855","a":[95,-21,1036]},{"t":"01-01-01T01:01:16.875","a":[94,-20,1033]},{"t":"01-01-01T01:01:16.890","a":[93,-20,1036]},{"t":"01-01-01T01:01:16.910","a":[93,-19,1033]},{"t":"01-01-01T01:01:16.929","a":[94,-20,1033]},{"t":"01-01-01T01:01:16.945","a":[96,-20,1036]},{"t":"01-01-01T01:01:16.964","a":[95,-22,1035]},{"t":"01-01-01T01:01:16.984","a":[95,-23,1033]},{"t":"01-01-01T01:01:16.000","a":[95,-25,1037]},{"t":"01-01-01T01:01:17.019","a":[93,-23,1038]},{"t":"01-01-01T01:01:17.035","a":[92,-21,1036]},{"t":"01-01-01T01:01:17.054","a":[91,-20,1034]},{"t":"01-01-01T01:01:17.074","a":[92,-21,1036]},{"t":"01-01-01T01:01:17.089","a":[91,-21,1037]},{"t":"01-01-01T01:01:17.109","a":[91,-19,1037]},{"t":"01-01-01T01:01:17.128","a":[90,-19,1035]},{"t":"01-01-01T01:01:17.144","a":[93,-20,1037]},{"t":"01-01-01T01:01:17.164","a":[95,-20,1037]},{"t":"01-01-01T01:01:17.183","a":[95,-19,1036]},{"t":"01-01-01T01:01:17.199","a":[95,-18,1036]},{"t":"01-01-01T01:01:17.218","a":[95,-20,1027]},{"t":"01-01-01T01:01:17.238","a":[85,-17,1012]},{"t":"01-01-01T01:01:17.253","a":[86,-18,1034]},{"t":"01-01-01T01:01:17.273","a":[90,-9,1084]},{"t":"01-01-01T01:01:17.289","a":[99,-30,1060]},{"t":"01-01-01T01:01:17.308","a":[108,-35,1018]}]}'

# Publicar el mensaje
mosquitto_pub -h $BROKER -p $PORT -t $TOPIC -m "$MESSAGE"

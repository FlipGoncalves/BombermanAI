#!/bin/bash

PORT=8000
if [ -n $1 ]
then
    PORT=$1
fi

rm ./highscores.json

for i in {1..100}
do
    echo Run $i
    NAME="BOMBERMAN" PORT=$PORT python ./reinforcementStudent.py
    sleep 3
done

var=$(cat ./highscores.json | json_pp | grep "\s\+[0-9]\+" | sed 's/ *$//g')
scores=($var)

sum=0
for (( c=0; c<100; c++ ))
do
    echo Score $c : ${scores[c]}
    sum=$(($sum + ${scores[c]}))
done

echo MÉDIA: $(($sum / 100))

eval "$(ps aux | awk '/server.py|viewer.py/ {printf "kill " $2 "\n"}')"

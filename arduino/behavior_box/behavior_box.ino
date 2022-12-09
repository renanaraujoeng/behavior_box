#include <Servo.h> 
#include <Thread.h>
#include <ThreadController.h>
 
const unsigned int MAX_MESSAGE_LENGTH = 12; //Maximun lenght of incoming message from USB

const int servoPin0 = 11; //Digital pin of servo 0 (Door Servo)
const int servoPin1 = 10; //Digital pin of servo 1 (Discrimination Servo Left)
const int servoPin2 = 6;  //Digital pin of servo 2 (Discrimination Servo Right)
const int servoPin3 = 3;  //Digital pin of servo 3 (Left Reward Servo)
const int servoPin4 = 5;  //Digital pin of servo 4 (Right Reward Servo)
const int rewardPump1 = 12; //Pump relay of left reward
const int rewardPump2 = 9; //Pump relay of right reward
const int sensorNoseDisc = 2; //Nose Poke Discrimination Sensor pin
const int sensorNoseLeft = 7; //Nose Poke Left Reward pin
const int sensorNoseRight = 4; //Nose Poke Right Reward pin
const int sensorDoor = 8; //Door Sensor
const int led = 13; //Arduino Led for debug

const int delayReadSensor = 100; //Time in ms to update the sensor values
const int delaySendSerial = 200; //Time in ms to send serial information
const int delayReadSerial = 100; //Time in ms to verifyu and read Serial information

//Struct with all Servo information
struct servo_struct {  
  Servo s; //Servo Object 
  int pos_current; //Current Position of Servo
  int positions[3];//All precalculated servo positions (0 - Open, 1 - Close, 2 - Large)
};

//Create array of servo structs
struct servo_struct servos[5];

//Auxiliary Global variables
int pos_final, pos_random; 
int p, i, j;
//Auxiliary Sensor Value variables
//int sensor_state;
int sensorNoseDiscValue = 0, sensorNoseLeftValue = 0, sensorNoseRightValue = 0, sensorDoorValue = 0;
int sensorNoseDiscValueLast = 2, sensorNoseLeftValueLast = 2, sensorNoseRightValueLast = 2, sensorDoorValueLast = 2;
int firstRead = 0;
int commandValue;
int intValue;
int delayRewardPump = 20; //Time in ms fo the reward pump activation

//Create a place to hold the incoming message
static char message[MAX_MESSAGE_LENGTH];
static unsigned int message_pos = 0;
char inByte;
String messageString;

//Initialize Threads
ThreadController control = ThreadController();
Thread readSensorsThread = Thread();
Thread sendSerialThread = Thread();
Thread readSerialThread = Thread();

//Function to be called with an interval to read the sensors regularly
void readSensors(){
  //Serial.println("-----READING SENSORS-----");
  firstRead = 1;
  sensorNoseLeftValue = digitalRead(sensorNoseLeft);
  sensorNoseRightValue = digitalRead(sensorNoseRight); 
  sensorNoseDiscValue = digitalRead(sensorNoseDisc);
  sensorDoorValue = digitalRead(sensorDoor);
}

//Function to send Serial data to USB
void sendSerial(){
  if(firstRead){
    if(sensorNoseDiscValue != sensorNoseDiscValueLast){
      Serial.print("p0=");
      Serial.println(sensorNoseDiscValue);
      sensorNoseDiscValueLast = sensorNoseDiscValue;
    }
    if(sensorDoorValue != sensorDoorValueLast){
      Serial.print("p1=");
      Serial.println(sensorDoorValue);
      sensorDoorValueLast = sensorDoorValue;
    }
    if(sensorNoseLeftValue != sensorNoseLeftValueLast){
      Serial.print("p2=");
      Serial.println(sensorNoseLeftValue);
      sensorNoseLeftValueLast = sensorNoseLeftValue;
    }
    if(sensorNoseRightValue != sensorNoseRightValueLast){
      Serial.print("p3=");
      Serial.println(sensorNoseRightValue);
      sensorNoseRightValueLast = sensorNoseRightValue;
    }   
  }
}

//Function to read Serial data from USB
//Commands: (disc=0, disc=1, disc=2), sX=0, sX=1, Where X=0 to 4. Ex: s0=0  
void readSerial(){
  //Serial.println("#####READING INFORMATION#####");
  while(Serial.available() > 0){
    //Read the next available byte in the serial receive buffer
    inByte = Serial.read();
    if (inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1)){
      //Add the incoming byte to our message
      message[message_pos] = inByte;
      message_pos++;
    }
    //Full message received...
    else
    {
      //Add null character to string
      message[message_pos] = '\0';

      //Print the message (or do other things)
      //Or convert to integer and print
      //int number = atoi(message);
      Serial.print("Message received = ");
      Serial.println(message);
      //Apply commands received from USB
      //Divide char array into two strings delimited by '='
      char * command = strtok(message, "=");
      char * value = strtok(NULL, "=");
      char * value2 = strtok(NULL, "\n");
      //Transform char array into integer 
      sscanf(value, "%d", &intValue); 
      if(strcmp(command,"disc") == 0){
        position_disc(intValue);
        // Serial.print("Disc Wall = ");
        // Serial.println(intValue);

      } else if (command[0] == 's'){
        //'s' command stands for servo
        //Transform single char into integer
        commandValue = command[1] - '0';
        position_servo(commandValue, intValue);
        // Serial.print("Servo ");
        // Serial.print(commandValue);
        // Serial.print(" to position ");
        // Serial.println(intValue);        
      } else if (command[0] == 'p'){
        //'p' command stands for pump
        sscanf(value2, "%d", &delayRewardPump);
        // Serial.print("Value = ");
        // Serial.println(value2);
        // Serial.print("DelayPump = ");
        // Serial.println(delayRewardPump);
        activate_pump(intValue);        
      } else if (command[0] == 'r'){
        //'r' command stands for reward
        reward(intValue);
        
      } 
      
      //Reset for the next message
      message_pos = 0;
   }
  }
}

//Function to position any servo to pre-calculated positions
void position_servo(int serv, int pos){
  Serial.print("-----SERVO ");
  Serial.print(serv);
  Serial.print(" TO POSITION ");
  Serial.print(pos);
  Serial.println("-----");
  pos_final = servos[serv].positions[pos];
  if(servos[serv].pos_current < pos_final){
    for(p = servos[serv].pos_current; p < pos_final; p++){
      servos[serv].s.write(p);
      delay(15);
    }
    servos[serv].pos_current = p;
  }else{
    for(p = servos[serv].pos_current; p > pos_final; p--){
      servos[serv].s.write(p);
      delay(15);
    }
    servos[serv].pos_current = p;
  }
}

void activate_pump(int pump){
  if(pump == 1){
    Serial.println("---LEFT PUMP---");
    digitalWrite(rewardPump1, HIGH);
    delay(delayRewardPump);
    digitalWrite(rewardPump1, LOW);
  } else if(pump == 2){
    Serial.println("---RIGHT PUMP---");
    digitalWrite(rewardPump2, HIGH);
    delay(delayRewardPump);
    digitalWrite(rewardPump2, LOW);
  }
}

//Position both discrimination servos to 0 - Closed, 1 - Wide, 2 - Open
void position_disc(int pos){
  if (pos == 0){ // Closed position
    Serial.println("---CLOSED TEST---");
    position_servo(1, 0);
    position_servo(2, 0);
  }else if(pos == 1){
    Serial.println("---WIDE TEST---");
    position_servo(1, 2);
    position_servo(2, 2);
  }else if(pos == 2){
    Serial.println("---OPEN TEST---");
    position_servo(1, 1);
    position_servo(2, 1);
  }
  
  
}

//Function to reward
void reward(int value){
  if(value == 1){
    Serial.println("-----REWARDING LEFT-----");
    position_servo(3, 1);
    activate_pump(1);
    delay(1000);
    position_servo(3, 0);  
  } else if (value == 2){
    Serial.println("-----REWARDING RIGHT-----");
    position_servo(4, 1);
    activate_pump(2);
    delay(1000);
    position_servo(4, 0);  
  }
}

//Function to open the main door
void open_door(){
  Serial.println("---DOOR OPEN---");
  position_servo(0, 1);
}

//Function to close main door
void close_door(){
  Serial.println("---DOOR CLOSED---");
  position_servo(0, 0);
}

void setup (){
  Serial.begin(9600); //Initialize Serial communication
  Serial.println("-----INITIALIZING SERVO VARIABLES-----");
  //Initialize servo struct values (Try and error for each servo)
  delay(1000);
  //Initializing Door Servo
  servos[0].pos_current = 45; //Variable for current position
  servos[0].positions[0] = 45; //Open Position
  servos[0].positions[1] = 165; //Closed Position
  servos[0].positions[2] = 45; //Large Position
  servos[0].s.attach(servoPin0); //Attach Servo pin to the Servo Object
  servos[0].s.write(servos[0].pos_current); //Write to initial Position
  //Initializing First Discrimination Servo
  servos[1].pos_current = 50;
  servos[1].positions[0] = 170;
  servos[1].positions[1] = 50;
  servos[1].positions[2] = 95;
  servos[1].s.attach(servoPin1);
  servos[1].s.write(servos[1].pos_current);
  //Initializing Second Discrimination Servo
  servos[2].pos_current = 120;
  servos[2].positions[0] = 0;
  servos[2].positions[1] = 120;
  servos[2].positions[2] = 75;
  servos[2].s.attach(servoPin2);
  servos[2].s.write(servos[2].pos_current);
  //Initializing Left Reward Servo
  servos[3].pos_current = 0;
  servos[3].positions[0] = 0;
  servos[3].positions[1] = 160;
  servos[3].positions[2] = 75;
  servos[3].s.attach(servoPin3);
  servos[3].s.write(servos[3].pos_current);
  //Initializing Right Reward Servo
  servos[4].pos_current = 160;
  servos[4].positions[0] = 160;
  servos[4].positions[1] = 0;
  servos[4].positions[2] = 75;
  servos[4].s.attach(servoPin4);
  servos[4].s.write(servos[4].pos_current);

  //Initialize Digital pins
  Serial.println("-----INITIALIZING PIN VARIABLES-----");
  pinMode(sensorNoseDisc, INPUT); //Define sensor pin as a digital input
  digitalWrite(sensorNoseDisc, HIGH); //Activate digital pullup
  pinMode(sensorNoseLeft, INPUT);
  digitalWrite(sensorNoseLeft, HIGH);
  pinMode(sensorNoseRight, INPUT);
  digitalWrite(sensorNoseRight, HIGH);
  pinMode(sensorDoor, INPUT);
  digitalWrite(sensorDoor, HIGH);
  pinMode(led, OUTPUT);
  pinMode(rewardPump1, OUTPUT);
  digitalWrite(rewardPump1, LOW);
  pinMode(rewardPump2, OUTPUT);
  digitalWrite(rewardPump2, LOW);
  //Initialize Threads  
  Serial.println("-----INITIALIZING THREADS-----");  
  readSensorsThread.onRun(readSensors);
  readSensorsThread.setInterval(delayReadSensor);
  sendSerialThread.onRun(sendSerial);
  sendSerialThread.setInterval(delaySendSerial);
  readSerialThread.onRun(readSerial);
  readSerialThread.setInterval(delayReadSerial);
  control.add(&readSensorsThread);
  control.add(&sendSerialThread);
  control.add(&readSerialThread);
}

void loop(){
  control.run();  
}
  
  

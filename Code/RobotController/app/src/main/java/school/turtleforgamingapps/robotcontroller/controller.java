package school.turtleforgamingapps.robotcontroller;

// Import of all module that are needed
import android.Manifest;
import android.app.ActivityManager;
import android.app.IntentService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.ArraySet;
import android.util.Log;
import android.view.Display;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.apache.commons.lang3.ArrayUtils;
import org.json.JSONObject;

import java.awt.font.TextAttribute;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.lang.reflect.Array;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.ConcurrentModificationException;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ExecutionException;

import io.github.controlwear.virtual.joystick.android.JoystickView;

//Main class
public class controller extends AppCompatActivity {

	//Initiate variables
    TextView statusLabel = null;
    TextView pingLabel = null;
    TextView dataLabel = null;
    WebView cameraFeed = null;
    JoystickView joystickCamera = null;
    JoystickView joystickMouvement = null;
    Button reloadUIbnt = null;
    Button restartConnectionbtn = null;
    Button quitBtn = null;
    Button audio_IsListeningBtn = null;
    Button audio_IsTalkingBtn = null;
    boolean audio_IsListening = false;
    boolean audio_IsTalking = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_controller);
        statusLabel = findViewById(R.id.statusTextView);				// Assign graphic element to the corresponding variable
        pingLabel = findViewById(R.id.pingTextView);					// Assign graphic element to the corresponding variable
        dataLabel = findViewById(R.id.dataTextView);					// Assign graphic element to the corresponding variable
        cameraFeed = findViewById(R.id.cameraFeedWebView);				// Assign graphic element to the corresponding variable
        cameraFeed.loadUrl("file:///android_res/raw/nofeed.html");  	//Load a temporary image to indicate that there is no video for now
        cameraFeed.getSettings().setJavaScriptEnabled(true);			//Enable javascript on the webview to enbale autorefresh
        cameraFeed.getSettings().setAppCacheEnabled(true);				//Enable cache for good mesure
        cameraFeed.getSettings().setLoadWithOverviewMode(true);
        cameraFeed.getSettings().setUseWideViewPort(true);
        cameraFeed.setVerticalScrollBarEnabled(false);					//Disable the scroll bar (vertical)
        cameraFeed.setHorizontalScrollBarEnabled(false);				//Disable the scroll bar (horizontal)
        //Make sure that we can't move the page
        cameraFeed.setOnTouchListener(new View.OnTouchListener() {@Override public boolean onTouch(View v, MotionEvent event) { return (event.getAction() == MotionEvent.ACTION_MOVE); }});
        //Display deault page if there is an error loading the supplyed video feed
        cameraFeed.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onReceivedTitle(WebView view, String title) {
                super.onReceivedTitle(view, title);
                CharSequence pnotfound = "HTTP error";
                if (title.contains(pnotfound)) {
                    Toast.makeText(view.getContext(), "Can't load video feed", Toast.LENGTH_LONG).show();	//Show the user that there is an error
                    view.loadUrl("file:///android_res/raw/nofeed.html");									//Load defualt page
                }
            }
        });
        //Display deault page if there is an error loading the supplyed video feed
        cameraFeed.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                Toast.makeText(view.getContext(), "Can't load video feed", Toast.LENGTH_LONG).show();	//Show the user that there is an error
                view.loadUrl("file:///android_res/raw/nofeed.html");									//Load defualt page
            }
        });
        joystickCamera = findViewById(R.id.cameraJoystick);		//Assing gui element to a variable
        joystickCamera.setOnMoveListener(new JoystickView.OnMoveListener() { //Set the action executed when the joystick position changes
            @Override
            public void onMove(int angle, int strength) {
            	// Create request: Ex: {"id":"controller","action":"joystick","type":"camera\","data":{"angle":90,"strenght":50}}
                String request = "{\"id\":\"controller\",\"action\":\"joystick\",\"type\":\"camera\",\"data\":{\"angle\":"+angle+",\"strenght\":"+strength+"}}";
                sendDataToSocket(request);
            }
        });
        joystickMouvement = findViewById(R.id.movementJoystick);	//Assing gui element to a variable
        joystickMouvement.setOnMoveListener(new JoystickView.OnMoveListener() {		//Set the action executed when the joystick position changes
            @Override
            public void onMove(int angle, int strength) {
            	// Create request: Ex: {"id":"controller","action":"joystick","type":"mouvement\","data":{"angle":90,"strenght":50}}
                String request = "{\"id\":\"controller\",\"action\":\"joystick\",\"type\":\"mouvement\",\"data\":{\"angle\":"+angle+",\"strenght\":"+strength+"}}";
                sendDataToSocket(request);
            }
        });
        reloadUIbnt = findViewById(R.id.btnReloadUI);	//Assing gui element to a variable
        reloadUIbnt.setOnClickListener(new View.OnClickListener() { //This fucntion allow the user to reload UI element that are server side by reasking the server for it
            @Override
            public void onClick(View v) {
                sendDataToSocket("{\"id\":\"controller\",\"action\":\"requestlivefeed\"}");
            }
        });
        restartConnectionbtn = findViewById(R.id.btnReconnect);		//Assing gui element to a variable
        restartConnectionbtn.setVisibility(View.INVISIBLE);			//Make it invisible because there isn't any error yet
        restartConnectionbtn.setEnabled(false);						//   ... Also disable it
        restartConnectionbtn.setOnClickListener(new View.OnClickListener() {	//Set the onclick function
            @Override
            public void onClick(View v) {
                restartConnectionbtn.setVisibility(View.INVISIBLE);		//Make the button invisible because there isn't any error yet
                restartConnectionbtn.setEnabled(false);					//   ... Also disable it
                statusLabel.setText("Link: Connecting ...");			//Display to the user that we are connecting
                myServiceBinder.RestsartThread();						// Restat the connection
            }
        });
        quitBtn = findViewById(R.id.quitBtn);						//Assing gui element to a variable
        quitBtn.setOnClickListener(new View.OnClickListener() {		//Set the onclick function
            @Override
            public void onClick(View v) {
                stopThread();										// Stop the background service
                finish();											// Quit the application
            }
        });
        String ip = getIntent().getStringExtra("ip");				//Get the server ip entered in the other activity
        int port = getIntent().getIntExtra("port",5000);			//    ... same for port
        String mode = getIntent().getStringExtra("mode");			//    ... and for the mode

        setJoystickMode(mode);										//Display joystick acording to the selected mode
        startThread(ip,port);										//Start the background service
        sInstance = this;

        audio_IsListeningBtn = findViewById(R.id.btnListen);
        audio_IsListeningBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                audio_toggleListening();
            }
        });
        audio_IsTalkingBtn = findViewById(R.id.btnMute);
        audio_IsTalkingBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                audio_toggleTalking();
            }
        });


        askPermission();

    }

    private static controller sInstance = null;						//Make an instance of ourselves so that an other function can change the ui
    public static controller getInstance() {						//This function return the current instance of the app
        return sInstance ;
    }

    public void askPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,Manifest.permission.RECORD_AUDIO)) {} else {
                ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.RECORD_AUDIO},1);
            }
        }
        if (ContextCompat.checkSelfPermission(this,Manifest.permission.INTERNET) != PackageManager.PERMISSION_GRANTED) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(this,Manifest.permission.INTERNET)) {} else {
                ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.INTERNET},1);
            }
        }
    }

    public static int getArrayIndex(int[] arr,int value,int def) {
        for(int i=0;i<arr.length;i++){ if(arr[i]==value){return i; }}
        return def;
    }
    public static String cutANullByte(String in) {
        return in.split("\0")[0];
    }
    private static class VBAN_Recv extends AsyncTask<Void, Void, String> {
        private WeakReference<controller> activityReference;
        public boolean serverActive = true;
        public String conf_streamName = "";
        public String conf_ipFrom = "";
        public Integer conf_srvPort = 6980;
        public Integer currentFrame = 0;

        // only retain a weak reference to the activity
        VBAN_Recv(controller context,String streamname,String ipfrom,Integer port) {
            activityReference = new WeakReference<>(context);
            conf_streamName = streamname;
            conf_ipFrom = ipfrom;
            conf_srvPort = port;
        }

        @Override
        protected String doInBackground(Void... params) {
            byte[] lMsg = new byte[2048];
            DatagramPacket dp = new DatagramPacket(lMsg, lMsg.length);
            int VBAN_SRList[]= {6000, 12000, 24000, 48000, 96000, 192000, 384000, 8000, 16000, 32000, 64000, 128000, 256000, 512000, 11025, 22050, 44100, 88200, 176400, 352800, 705600};
            try {
                DatagramSocket ds = new DatagramSocket(conf_srvPort);

                int originalBufsize = AudioTrack.getMinBufferSize(48000, AudioFormat.CHANNEL_OUT_STEREO,AudioFormat.ENCODING_PCM_16BIT);
                AudioTrack at = new AudioTrack(AudioManager.STREAM_MUSIC,48000,AudioFormat.CHANNEL_OUT_STEREO,AudioFormat.ENCODING_PCM_16BIT,originalBufsize, AudioTrack.MODE_STREAM );
                at.play();

                while (serverActive)  {
                    ds.receive(dp);

                    byte[] rawData = dp.getData();

                    String  magicString = new String(lMsg,0,dp.getLength()).substring(0,4);
                    Integer sampleRate  = VBAN_SRList[(int)new String(lMsg,4,1).getBytes()[0]];
                    Integer format_bit  = (int)new String(lMsg,7,1).getBytes()[0];
                    ByteBuffer wrapped = ByteBuffer.wrap(rawData);
                    wrapped.order(ByteOrder.LITTLE_ENDIAN);
                    Integer channCount = (int)wrapped.getShort(6)-255;
                    Integer sampleCount = (int)wrapped.getShort(5) / channCount;
                    String  streamName  = cutANullByte(new String(lMsg,8,16));
                    Integer frameCounter = (int)wrapped.getLong(24);
                    String data2 = magicString+" SR:"+sampleRate.toString()+"Hz "+sampleCount+"samps "+channCount+"Chans BitResolution:"+format_bit+" Streamname:"+streamName+" Frame:" +frameCounter;

                    currentFrame = frameCounter;

                    //Log.wtf("t",data2);
                    int buffsize;
                    int channcount;
                    if (channCount==1) {
                        buffsize = AudioTrack.getMinBufferSize(sampleRate, AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT);
                        channcount =  AudioFormat.CHANNEL_OUT_MONO;
                    } else {
                        buffsize = AudioTrack.getMinBufferSize(sampleRate, AudioFormat.CHANNEL_OUT_STEREO, AudioFormat.ENCODING_PCM_16BIT);
                        channcount =  AudioFormat.CHANNEL_OUT_STEREO;
                    }

                    if(originalBufsize != buffsize) {
                        originalBufsize = buffsize;
                        at.stop();
                        at.release();
                        at = new AudioTrack(AudioManager.STREAM_MUSIC,
                                sampleRate, //sample rate
                                channcount, //2 channel
                                AudioFormat.ENCODING_PCM_16BIT, // 16-bit
                                originalBufsize,
                                AudioTrack.MODE_STREAM );
                        at.play();
                    }

                    if(conf_streamName.equals(streamName)) {
                        if(conf_ipFrom.equals(dp.getAddress().getHostAddress())) {
                            byte[] pcmData = Arrays.copyOfRange(rawData, 28, dp.getLength());
                            at.write(pcmData, 0, pcmData.length);
                        }
                    }

                    //Log.wtf("TAGG",streamName+":"+conf_streamName);

                    //MainActivity activity = activityReference.get();
                    //if (activity == null || activity.isFinishing()) break;
                    //TextView textView = activity.findViewById(R.id.textView1);
                    //textView.setText("Magic: "+data2);
                }
                at.stop();
                at.release();
                ds.close();

            } catch (Exception e) {Log.e("DatagramSocket","DatagramSocket failed",e);}
            return "task finished";
        }

        @Override
        protected void onPostExecute(String result) {
            //Nothing here
        }
    }
    private static class VBAN_Send extends AsyncTask<Void, Void, String> {
        private WeakReference<controller> activityReference;
        public boolean serverActive = true;
        public String conf_streamName = "";
        public String conf_ipTo = "";
        public Integer conf_srvPort = 6980;
        public Integer conf_sampleRate = 0;
        public int conf_channels = 0;
        public Integer currentFrame = 0;

        // only retain a weak reference to the activity
        VBAN_Send(controller context,String streamname,String ipto,Integer port,Integer samprate,Integer channels) {
            activityReference = new WeakReference<>(context);
            conf_streamName = streamname;
            conf_ipTo = ipto;
            conf_srvPort = port;
            conf_channels = channels;
            conf_sampleRate = samprate;
        }

        @Override
        protected String doInBackground(Void... params) {
            int VBAN_SRList[]= {6000, 12000, 24000, 48000, 96000, 192000, 384000, 8000, 16000, 32000, 64000, 128000, 256000, 512000, 11025, 22050, 44100, 88200, 176400, 352800, 705600};
            try {

                DatagramSocket ds = new DatagramSocket(conf_srvPort);
                InetAddress ip = InetAddress.getByName(conf_ipTo);

                int audioformat = AudioFormat.CHANNEL_IN_STEREO;
                if (conf_channels == 1) { audioformat=AudioFormat.CHANNEL_IN_MONO; }

                int bufferSize = 1024;
                AudioRecord record = new AudioRecord(MediaRecorder.AudioSource.MIC,conf_sampleRate,audioformat,AudioFormat.ENCODING_PCM_16BIT,bufferSize);
                record.startRecording();


                byte[] headerData = new byte[28];
                headerData[0] = 'V';
                headerData[1] = 'B';
                headerData[2] = 'A';
                headerData[3] = 'N';
                headerData[4] = (byte) getArrayIndex(VBAN_SRList,conf_sampleRate,3);
                headerData[5] = (byte) 0xFF;
                headerData[6] = (byte) (conf_channels -1);
                headerData[7] = '\1';
                int i=8;
                for (char c:conf_streamName.toCharArray()) {  headerData[i] = (byte)c; i++;}
                for (; i < 24; i++) { headerData[i] = '\0'; }


                while (serverActive)  {
                    currentFrame++;
                    byte[] pcmData =  new byte[bufferSize];

                    ByteBuffer b = ByteBuffer.allocate(4);
                    b.order(ByteOrder.LITTLE_ENDIAN);
                    b.putInt(currentFrame);

                    byte[] tmp = b.array();
                    headerData[24] = tmp[0];
                    headerData[25] = tmp[1];
                    headerData[26] = tmp[2];
                    headerData[27] = tmp[3];

                    record.read(pcmData, 0, pcmData.length);

                    byte[] data = ArrayUtils.addAll(headerData, pcmData);
                    DatagramPacket sent_packet = new DatagramPacket(data,data.length, ip, conf_srvPort);
                    try {
                        ds.send(sent_packet);
                    } catch (IOException e) { Log.e("VBAN_Send","IOExeption",e); }
                }
                ds.close();
                record.release();
                record.stop();

            } catch (Exception e) {
                Log.e("DatagramSocket","DatagramSocket failed",e);}
            return "task finished";

        }

        @Override
        protected void onPostExecute(String result) {
            //Nothing here
        }
    }
    public VBAN_Send myVBAN_Task_Send = null;
    public VBAN_Recv myVBAN_Task_Recv = null;
    public void audio_toggleListening() {
        String ip = getIntent().getStringExtra("ip");
        if(myVBAN_Task_Recv == null) {
            myVBAN_Task_Recv = new VBAN_Recv(this,"Robot",ip,6981);
            myVBAN_Task_Recv.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            audio_IsListeningBtn.setBackground(getDrawable(R.mipmap.ic_listeing));
        } else {
            myVBAN_Task_Recv.serverActive = false;
            myVBAN_Task_Recv = null;
            audio_IsListeningBtn.setBackground(getDrawable(R.mipmap.ic_dontlisten));
        }
    }
    public void audio_toggleTalking() {
        String ip = getIntent().getStringExtra("ip");
        if(myVBAN_Task_Send == null) {
            myVBAN_Task_Send = new VBAN_Send(this,"Robot",ip,6980,48000,2);
            myVBAN_Task_Send.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
            audio_IsTalkingBtn.setBackground(getDrawable(R.mipmap.ic_talking));
        } else {
            myVBAN_Task_Send.serverActive = false;
            myVBAN_Task_Send = null;
            audio_IsTalkingBtn.setBackground(getDrawable(R.mipmap.ic_muted));
        }
    }

    public void setJoystickMode(String mode) {
        if(mode.equals("Mouvement")) {							// We only show the joystick responcable for moving the robot
            joystickCamera.setEnabled(false);
            joystickCamera.setVisibility(View.INVISIBLE);
            joystickMouvement.setEnabled(true);
            joystickMouvement.setVisibility(View.VISIBLE);
        } else if(mode.equals("Camera")) {						// We only show the joystick responcable for moving the camera
            joystickCamera.setEnabled(true);
            joystickCamera.setVisibility(View.VISIBLE);
            joystickMouvement.setEnabled(false);
            joystickMouvement.setVisibility(View.INVISIBLE);
        } else  {												// We only show all joysticks 
            joystickCamera.setEnabled(true);
            joystickCamera.setVisibility(View.VISIBLE);
            joystickMouvement.setEnabled(true);
            joystickMouvement.setVisibility(View.VISIBLE);
        }
    }
    boolean itsOKtoSend = true;
    public void dataFromSocket(String text) {					//This function prase the data comming from the robot
        try{
            //{"action":"setlivefeed","data":{"url":"https://img-31.ccm2.net/aoRGBEGGQk_4JKu7HmX1rD12M58=/1240x/smart/0476616b609244458962620520ffe5e6/ccmcms-hugo/10605741.jpg"}}
            JSONObject reader = new JSONObject(text);
            String action = reader.getString("action");
            if(action.equals("setlivefeed")) {					//THe robot tell us the adress of the video feed
                JSONObject data  = reader.getJSONObject("data");//Decode the json
                String URL = data.getString("url");				//Get the url
                sendDataToSocket(URL);							// Hummmm ACK I think
                cameraFeed.loadUrl(URL);						// Load the the feed into the webview
            }
            if(action.equals("pingcalculation")) {											//Robot tell us at which time a message was sent to calculate latency
                JSONObject data  = reader.getJSONObject("data");							//Decode JSON
                Long t = data.getLong("time");												//Get the time at which the message was sent
                int lag = Integer.parseInt(String.valueOf(System.currentTimeMillis()-t));	// Calculate the difference between now at the sent time.
                pingLabel.setText(String.valueOf(lag)+" ms");								// Display the lag
                if(lag > 1000) { pingLabel.setTextColor(Color.RED); }						//Change the text color to red if more that 1sec of latency
                else if(lag > 500) { pingLabel.setTextColor(Color.YELLOW); }				//Change the text color to yellow if more that 0.5sec of latency
                else { pingLabel.setTextColor(Color.GREEN); }								//Change the text color to green otherwise
            }
            if(action.equals("freedata")) {							//That text that the robot can display on the app
                JSONObject data  = reader.getJSONObject("data");	//Decode JSON
                String t = data.getString("text");					// get the text
                dataLabel.setText(t);								//    .... Display it
            }

        } catch (Exception e) { 		//If there is an error print it and continue
            e.printStackTrace();
            Log.wtf("JSONPraseError",text,e);
            Log.wtf("JSONPraseError",text);
        }
    }
    long lastPAcket = System.currentTimeMillis();

    public void sendDataToSocket(String txt) {			//This function send data to the robot
        if (myService != null ) {						//Check if the service is actually started and binded to the gui
            long cc = System.currentTimeMillis();
            if(cc > lastPAcket+50) {
                myServiceBinder.sendDataToSocket(txt); //outGoingDataQueue.add(txt);
                lastPAcket = cc;
            }
        }
    }

    public void exceptionManager(final String activity,final String tag, final String function, final Exception e) {	//Beautiful log displaying for debuging
        Log.wtf(tag, "[" + activity + " / "+function+"] " + e.getMessage());
    }

    public boolean isMyServiceRunning(Class<?> serviceClass) {		//Check if a service is started
        ActivityManager manager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        for (ActivityManager.RunningServiceInfo service : manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.getName().equals(service.service.getClassName())) {
                return true;
            }
        }
        return false;
    }

    public void startThread(String ip,int port) {				//Start the bacgound service
        Intent i = new Intent(this, socketService.class);		// Generate intent
        i.putExtra("addr",ip);									// and the server ip
        i.putExtra("port",port);								//    ... And port
        startService(i);										// Start it
        if (myService == null) { doBindService(); }				// Bind it to the gui
        if (myService == null) { doBindService(); }				// 2times to be sure
        if (myService == null) { doBindService(); }				// 3times for good mesure
    }
    public void stopThread() {														//Stop the background service
        if (myService != null) {  unbindService(myConnection); myService = null; }	// If the service is bound to gui unbound it before destroying it
        stopService(new Intent(this, socketService.class));							// Stop the service
    }

    public socketService myServiceBinder;		//Variable that hold's the serivce binder
    public ServiceConnection myService = null;	//Variable that hold's the bound service
    public ServiceConnection myConnection = new ServiceConnection() {
        public void onServiceConnected(ComponentName className, IBinder binder) {	// Funtion executed when the service is bound
            myServiceBinder = ((socketService.MyBinder) binder).getService();		// Store the service instance in a variable
            Log.d("WifiService_Conne","connected");							// Logggg
            myService = myConnection;												// Store the connection to the service
        }

        public void onServiceDisconnected(ComponentName className) {				// Function executed when the service is unbound / disconnected
            Log.d("WifiService_Disco","disconnected");						// Logggg
            myService = null;														// Set the connection to a null value
        }
    };
    public Handler myHandler = new  Handler() {  public void handleMessage(Message message) { Bundle data = message.getData(); } };  //Don'tknow what it is

    public void onDestroy() {	//Executed when the window is closed
        super.onDestroy();		//
        stopThread();			// Stop the service
    }
    public void doBindService() {																//Function used to bind the service
        try {																					//Alwas use a trycatch
            Intent intent = null;																//Create an empty intent
            intent = new Intent(this, socketService.class);										//Set it to the service
            Messenger messenger = new Messenger(myHandler);										// Create a new Messenger for the communication back From the Service to the Activity
            intent.putExtra("MESSENGER", messenger);											//   ... Join it to the intent
            bindService(intent, myConnection, Context.BIND_AUTO_CREATE);						// Bind the intent to the variable myConnection
        } catch(Exception e) { exceptionManager("controller","BIND","doBindService",e); }
    }
}

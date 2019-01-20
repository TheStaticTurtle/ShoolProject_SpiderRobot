package school.turtleforgamingapps.robotcontroller;

// Import of all module that are needed
import android.app.ActivityManager;
import android.app.IntentService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.os.Messenger;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
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

import org.json.JSONObject;

import java.awt.font.TextAttribute;
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
    }

    private static controller sInstance = null;						//Make an instance of ourselves so that an other function can change the ui
    public static controller getInstance() {						//This function return the current instance of the app
        return sInstance ;
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
        }
    }
    public void sendDataToSocket(String txt) {			//This function send data to the robot
        if (myService != null) {						//Check if the service is actually started and binded to the gui
            myServiceBinder.sendDataToSocket(txt);		//     ... Send
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
            Log.d("WifiService_Connection","connected");							// Logggg
            myService = myConnection;												// Store the connection to the service
        }

        public void onServiceDisconnected(ComponentName className) {				// Function executed when the service is unbound / disconnected
            Log.d("WifiService_Disconnection","disconnected");						// Logggg
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

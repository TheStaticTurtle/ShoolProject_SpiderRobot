package school.turtleforgamingapps.robotcontroller;

import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Binder;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Messenger;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.UnknownHostException;

public class socketService extends Service {
	//Inititate variable
    socketService thisservice = this;
    Handler handler;
    String srvAddr="";
    private ConnectedThread mConnectedThread;
    String  srvAddress ="";
    int     srvPort = -1;
    private Socket socket;
    PrintWriter socketPrintWriter;
    controller UIInstance = null;

    public socketService() { }

    private void runOnUiThread(Runnable runnable) {	//Function used to modify gui
        handler.post(runnable);
    }

    @Override public void onCreate() {				//Function executed when the service start
        handler = new Handler();
        Toast.makeText(this, "The new Service was Created", Toast.LENGTH_SHORT).show();
    }

    @Override public void onDestroy() { }

    public void RestsartThread() {					//Function used to reconnect to the server
        ConnectSocket t = new ConnectSocket();
        t.execute(); //Call the class to connect
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {	//Executed when the service receive a start command
        try {
            Bundle extras = intent.getExtras();				//Get the sent extras
            if (extras != null) {
                srvAddress = (String) extras.get("addr");	//IP
                srvPort = (int) extras.get("port");			//PORT
                ConnectSocket t = new ConnectSocket();		//Initiate a async task to connect to the server
                t.execute(); 								//Call the class to connect
            } else {
                exceptionManager("SRV_START","onStartCommand","onStartCommand",new Exception("extras = null"));	//Logggg
            }
            return START_NOT_STICKY;	//Make sure that the service doesn't close when the app close
        } catch(Exception e) { exceptionManager("SRV_START","onStartCommand","onStartCommand",e); }	//Logggg
        return START_NOT_STICKY;		//Make sure that the service doesn't close when the app close
    }

    private boolean ConnectSuccess = true; //Set it to true from the beginin and if there is an error set it to false
    private class ConnectSocket extends AsyncTask<Void, Void, Void>  /* UI Thread class */ {
        @Override protected void onPreExecute(){} //No need for a prexecute
        @Override protected Void doInBackground(Void... devices) //while the progress dialog is shown, the connection is done in background
        {
            ConnectSuccess = true;		//Make sure that it is true
            try {
                SocketAddress serverAddr = new InetSocketAddress(srvAddress, srvPort);	//Create the server adress instance
                socket = new Socket();													//Create the socket
                socket.setSoTimeout(2000);												//Set the timeout to 2sec
                socket.connect(serverAddr);												//Connect
                socketPrintWriter = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())),true); //Create a printwriter to be able to send data / receive
                isLastPacketSended = true;	//Make sure to reinit this varible so that a new packet can be sent
            } catch (Exception e1) {
                e1.printStackTrace();
                ConnectSuccess = false;//if the try failed, you can check the exception here
            }
            return null;
        }
        @Override
        protected void onPostExecute(Void result) //after the doInBackground, it checks if everything went fine
        {
            super.onPostExecute(result);

            if (!ConnectSuccess){
                exceptionManager("BLE_CONN","ConnectBT","onPostExecute",new Exception("Can't reach client"));	//Loggg
                updateUI();																						//Notify the user
            }else{
                mConnectedThread = new ConnectedThread(socket);	//Initiate a background thread
                mConnectedThread.start();						//Start a background thread
            }
        }
    }

    private class ConnectedThread extends Thread {
        private InputStream mmInStream = null;	//Create a empty stream to receive data

        public ConnectedThread(Socket s) {
            InputStream tmpIn = null;			//Make sure that it's initiated
            try {
                tmpIn = s.getInputStream();		//Get the current stream and assing it
                mmInStream = tmpIn;
            } catch (IOException e) {
                e.printStackTrace();	//Loggg
            }
        }

        public void run() {
            byte[] buffer = new byte[4096];		//Create an empty buffer to store data
            int bytes;							//Create an empty int to store the number of byte received
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND);	//Set the thread as a background thread
            Looper.prepare();																		// ???
            while (mmInStream!=null) {																// If the stream isn't brocken
                try {
                    if (mmInStream.available() > 1) {												//If data is avalible
                        try {sleep(100);} catch (InterruptedException e) {e.printStackTrace();}		//Wait a bit to ensure that all data has been received
                        bytes = mmInStream.read(buffer); 											//read bytes from input buffer
                        final String readMessage = new String(buffer, 0, bytes);					//Convert the recevied bytes to a string
                        runOnUiThread(new Runnable() {												//Execute a function on the UI / GUI the get out of the background thread (For modifing ui elements)
                            @Override
                            public void run() {
                                //Toast.makeText(socketService.this, readMessage, Toast.LENGTH_LONG).show();
                                UIInstance = controller.getInstance();
                                if(UIInstance!=null) {
                                    UIInstance.dataFromSocket(readMessage);
                                }
                            }
                        });
                    }
                } catch (Exception e) {
                    e.printStackTrace();	//Log
                    mmInStream=null;		//Stream is probably brocken so reset it
                }
                updateUI();
                try {sleep(50);} catch (InterruptedException e) {e.printStackTrace();}
                //Log.e("closed",String.valueOf(socket.isClosed()));
            }
            //Log.e("closed",String.valueOf(socket.isClosed()));
        }
    }

    private void socketAlive(Socket s) {				//Unused
        sendDataToSocket("{\"action\",\"null\"}");
    }

    boolean isLastPacketSended = true;												//Initialize lock variable
    private class SendToSocket extends AsyncTask<String, Integer, Integer> {		//Async task										
        protected Integer doInBackground(String... test) {							//Background task
            try {
                socketPrintWriter.println(test[0]);									//Send the data
                if(socketPrintWriter.checkError())  {
                    throw new Exception("Error transmitting data.");				//Can't send data
                }
                Thread.sleep(1);													//Sleep
            } catch (Exception e1) {
                e1.printStackTrace();												//Loggg
                try {socket.close();} catch (Exception e) {e.printStackTrace();}	//Close socket for good mesure
            }
            isLastPacketSended = true;												//Tell that le packet has been sent
            return  1;
        }

        protected void onPostExecute(Integer result) { }
    }

    public void sendDataToSocket(String test) {			//Function used to start the async task
        if(isLastPacketSended && !socket.isClosed()) { 	//Avoid sending older packet after a newer one
            isLastPacketSended = false;					//Set that the message isn't sent
            SendToSocket t = new SendToSocket();		//Prepare the Async task
            t.execute(test);							//Start it
        }
    }

    public void updateUI() {
        UIInstance = controller.getInstance();															//Get the UI instance to be able to access ui element
        if(UIInstance!=null) {																			//Verify that it isn't empty
            runOnUiThread(new Runnable() {																//Create a new runable to run on the ui thread
                @Override
                public void run() {
                    if(socket != null) {																//If the socket is open
                        if(!socket.isClosed() && ConnectSuccess) { if(UIInstance.statusLabel!=null) {	//	...And the text instance isn't null
                            UIInstance.statusLabel.setText("Link: Connected");							// Display that we are conected
                            UIInstance.statusLabel.setTextColor(Color.GREEN);							//	...In green	
                        }}
                        if(socket.isClosed()) { if(UIInstance.statusLabel!=null) {						//If the socket is open
                            UIInstance.statusLabel.setText("Link: Disconnected");						// Display that we aren't conected
                            UIInstance.statusLabel.setTextColor(Color.RED);								//	...In red
                            UIInstance.restartConnectionbtn.setVisibility(View.VISIBLE);				//	... and show the reconnect button
                            UIInstance.restartConnectionbtn.setEnabled(true);
                        }}
                    }
                    if(!ConnectSuccess) { if(UIInstance.statusLabel!=null) {							//If we didn't connect
                        UIInstance.statusLabel.setText("Link: Timeout / Error");						// Display that there is an error
                        UIInstance.statusLabel.setTextColor(Color.RED);									//	..In red
                        UIInstance.restartConnectionbtn.setVisibility(View.VISIBLE);					//	... and show the reconnect button
                        UIInstance.restartConnectionbtn.setEnabled(true);
                    }}
                }
            });
        }
    }

    private final IBinder mBinder = new MyBinder();									//Create a binder
    @Override
    public IBinder onBind(Intent arg0) {											//Override the defualt onbind function
        Bundle extras = arg0.getExtras();											//Get extras
        Log.d("service","onBind");													//Logggg
        // Get messager from the Activity
        if (extras != null) {														//If there is extras
            Log.d("service","onBind with extra");									//Loggg
            Messenger outMessenger = (Messenger) extras.get("MESSENGER");			//Get the messenger sent from the UI
        }
        return mBinder;
    }
    public class MyBinder extends Binder {
        socketService getService() {
            return socketService.this;
        }
    }
    public boolean onUnbind() { /* throw new RuntimeException("Stub!"); */ return true;}


    public void exceptionManager(final String activity,final String tag, final String function, final Exception e) {
        Log.wtf(tag, "[" + activity + " / "+function+"] " + e.getMessage());	//Logggggg
    }

}

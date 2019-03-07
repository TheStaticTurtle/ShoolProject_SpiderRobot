package school.turtleforgamingapps.robotcontroller;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;

public class startupScreen extends AppCompatActivity {

    EditText ipaddrET = null;		//Holder for gui element
    EditText portaddtET = null;		//Holder for gui element
    Spinner modeSpinner = null;		//Holder for gui element

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_startup_screen);										//Set correct layout
        ipaddrET = findViewById(R.id.etIPAddr);													//Assign gui element to holder
        portaddtET = findViewById(R.id.etPORTAddr);												//Assign gui element to holder
        modeSpinner = findViewById(R.id.spinnerModeSelctor);									//Assign gui element to holder
        Button btn = findViewById(R.id.btnConnect);												//Assign gui element to holder
        btn.setOnClickListener(new View.OnClickListener() {										//Set a onlclick listener
            @Override
            public void onClick(View v) {
                Intent controller = new Intent(startupScreen.this, controller.class);			//Create new intent to start the controller
                controller.putExtra("ip",ipaddrET.getText().toString());						//Join the ip of the server to the intent
                controller.putExtra("port",Integer.valueOf(portaddtET.getText().toString()));	//Join the port of the server to the intent
                controller.putExtra("mode",modeSpinner.getSelectedItem().toString());			//Join the mode of the server to the intent
                startActivity(controller);														//Start the activity
            }
        });
    }
}

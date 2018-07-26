//
// MakeNetwork.cs
// 
// This file contains the main computational model logic. Using standard Unity hooks, it interfaces with ThirdPersonController and MNI1 for Avatar Logic and pretty display things 
//

using System.Collections;
using System.IO;
//using System;
using UnityEngine;
using System.Text.RegularExpressions;
using UnityEngine.UI;
using System.Linq;
using UnityStandardAssets.Characters.ThirdPerson;
using HelperScripts;


namespace MakeNetworkNamespace
{
public class ModelLogic : MonoBehaviour {

		// Set up a bunch of variables for the model as well as some unity hooks for the interface.

		// Initialise Conectity Matrix
		private int N=66;

		// Hard coded 66 Region connectivity matrix (Hagmann 2011)
		private float[,] CBase;
		private float[,] Locations;
		private int[,] C= new int[66,66];
		private double[,] CBaseAdapt = new double[66,66];
		private double SumCBase;
		public float Conn_Thresh=0.0f; // Threshold for connectivity matrix.

		// Initialisation of Computational Model parameters
		public int[] RandomIndices = new int[33];
		public bool RandomRegion;
		public float pQE; // the probability of a quiescent region Exciting at a given time
		public float pER; // probability of Excitatory neuron becoming refractory
		public float pRQ; // the probability of a refractory neuron becoming quiescent
		public int tF = 1; // the time duration of firing
		public float Thr; // Threshold at which sum total of neighbours activity causes you to fire
		public int Quiescent = 1; 
		public int Excitatory = 2; 
		public int Refractory = 3;
		public bool Memmode;

		public float Str = 100; // scaling factor for the connectivity matrix.

		private float MaxStates;
		private float MinStates;
		public bool Move = true; // TODO: what is this?
		public float Crow=0;
		private float timeOld;


		// Vectors to store model states in.
		public int[] StatesNow = new int[66];
		public float[] ThrArray = new float[66];
		private int[] StatesPrevious = new int[66]; 
		public int[] StatesSelected = new int[66]; 
		public float[] StatesAv = new float[66]; // this guy holds the average states over time.

		private float oldThrVal;
		private string SNpath; 
		private string SSpath; 
		private string Locpath; 
		private string Thrpath;
		private string Paramspath;
		public bool OffLineBuild = true; // choose if to save out data or not.
		public bool Somatosensory = true; // this, a flag to totally turn off somatosensory stuff (For debug and somewhat nefarious nonsense).

		// Unity Hooks (LHS Render)
		public GameObject NetworkNode; // Object to be used for nodes in the model render on LHS
		public GameObject NodeText; // Object to be used for labels in render on LHS
		public GameObject LineBase; // Object to be used for connectivtiy lines in render on LHS
		public GameObject Input_Labels; // Interface Toggle box for showing labels in render on LHS
		public Material NodeMaterial; // Material for Node Objects
		public Material NodeMaterialSelected; // Material for activiated nodes.
		private Renderer TempNode;
		private LineRenderer TempLine;
		public int[,] LineIndex= new int[66, 66];
		public Color c1 = Color.white;
		public Color c2 = Color.white;
		public Color c3 = Color.red;
		public int lengthOfLineRenderer;
		private int Count=0;
		public float lr=0.01f;
		public float tr=0.01f;
		public float HistoryLength=10.0f; // this controls convolution of data for learning rule.
		public int randomseed=1;
		private int filenumber = 1;

		// Unity Hooks (User Interface)
		public GameObject SpeedSlider; // Interface object to change model speed
		public GameObject Input_Homeo; // Interface Toggle box for local homeostais
		public GameObject TargRate; // Interface object to change target rate
		public GameObject Input_TN; // Interface Toggle box for switching Task Negative
		public GameObject Input_PQE; // Interface object to change PQE value
		public GameObject Input_Thresh; // Interface object to change Threshold value
		public GameObject ForageController; //Interface object to forage controller.

		// Unity Hooks (Avatar)
		public GameObject GameAvatar;
		public Camera MainCamera;
		public Camera FigureCamera;

		// Housekeeping parameters
		private bool started=false;
		public bool OptionsOn=true; //TODO: Remove OptionsOn Logic
		public float ModelUpdateInterval;
		public bool Homeo;
		public bool TN;
		public float T; //Value for remembering current T.
		public int tmax; // maximum value for T.

		Arguments CommandLine=new Arguments(System.Environment.GetCommandLineArgs()); // get and parse command line arguments.

		void Start () {
			if(CommandLine["randomseed"] != null){
				randomseed = int.Parse (CommandLine ["randomseed"]);
			}

			Random.InitState (randomseed);
			CBase = HelperScripts.IO.readCSV("connectivity"); // Read Hagmann matrix from file.
			Locations =  HelperScripts.IO.readCSV("locations"); // Read MNI coordinates of aparc segmentation from file.
			N = 66;

			// Stuff that gets done right as the game starts. Before any Frames are rendered.
			Application.runInBackground = true;

			// Define the regions of the model that are used for TP TN node (Defaults below)
			RandomRegion = false;
			RandomIndices [0] = 23; // Direction Node
			RandomIndices [1] = 15; // Forward Motor Node
			RandomIndices [2] = 20; // Eye near IN
			RandomIndices [3] = 10; // Eye far IN
			RandomIndices [4] = 21; // collider IN
			RandomIndices [5] = 9; // visual TN
			RandomIndices [6] = 22; // collider TN
			//Debug.LogError("Logging is Swithced on!");
			// Overwrite these values with command line parameters if needed.
			if(CommandLine["forward"] != null){
				RandomIndices [1] = int.Parse (CommandLine ["forward"]);
			}
			if(CommandLine["direction"] != null){
				RandomIndices [0] = int.Parse (CommandLine ["direction"]);
			}
			if(CommandLine["neareye"] != null){
				RandomIndices [2] = int.Parse (CommandLine ["neareye"]);
			}
			if(CommandLine["fareye"] != null){
				RandomIndices [3] = int.Parse (CommandLine ["fareye"]);
			}
			if(CommandLine["collider"] != null){
				RandomIndices [4] = int.Parse (CommandLine ["collider"]);
			}
			if(CommandLine["visualTN"] != null){
				RandomIndices [5] = int.Parse (CommandLine ["visualTN"]);
			}
			if(CommandLine["colliderTN"] != null){
				RandomIndices [6] = int.Parse (CommandLine ["colliderTN"]);
			}
			if(CommandLine["SS_OFF"] != null){
				Somatosensory = false;
			}
			// some Rendering variables
			lengthOfLineRenderer = 2;

			// Display a bunch of the interface
			Input_Homeo.SetActive (OptionsOn);
			Input_PQE.SetActive (OptionsOn);
			Input_Thresh.SetActive (OptionsOn);
			SpeedSlider.SetActive (OptionsOn);
			Input_Labels.SetActive (OptionsOn);
			Input_TN.SetActive (OptionsOn);
			TargRate.SetActive (OptionsOn);

			// set some threshold values (can later be updated from the sliders)
			pQE = 0.01f;
			pER = 1.0f;
			pRQ = 1f;
			Thr = 4f;

			if(CommandLine["pQE"] != null){
				if (float.TryParse(CommandLine["pQE"],out pQE)){
				}
			}
			if(CommandLine["pER"] != null){
				if (float.TryParse(CommandLine["pER"],out pER)) {
				}
			}
			if(CommandLine["pRQ"] != null){
				if (float.TryParse(CommandLine["pRQ"],out pRQ)) {
				}
			}
			if(CommandLine["Thr"] != null){
				if (float.TryParse(CommandLine["Thr"],out Thr)) {
				}
			}
			if(CommandLine["lr"] != null){
				if (float.TryParse(CommandLine["lr"],out lr)) {
				}
			}
			if(CommandLine["HistoryLength"] != null){
				if (float.TryParse(CommandLine["HistoryLength"],out HistoryLength)) {
				}
			}
			Input_Thresh.GetComponent<Slider> ().value = Thr;
			Input_PQE.GetComponent<Slider> ().value = pQE;

			oldThrVal = Thr;
			ModelUpdateInterval = 0.1f;
			T = 0;
			tmax = int.MaxValue;

			if(CommandLine["tmax"] != null){
				if (int.TryParse(CommandLine["tmax"],out tmax)) {
				}
			}

			if(CommandLine["Str"] != null){
				if (float.TryParse(CommandLine["Str"],out Str)) {
				}
			}

			timeOld = Time.time;
			c1 = Color.white;
			c2 = Color.white;
			c3 = Color.red;
			Homeo = false;
			TN = false;
			tr = 0.1f; // target rate for local homeostasis.
			Memmode = true;
			if(CommandLine["memmode"] != null){
				if (CommandLine ["memmode"] == "false") {
					Memmode = false; 
				} else{
					if (float.TryParse(CommandLine["memmode"],out tr)) {
						Memmode = true; //  set output to avoid re-reading a bunch of files.
					}
				}
			}

			if(CommandLine["Homeo"] != null){
				if (CommandLine ["Homeo"] == "false") {
					Homeo = false; 
				} else{
					if (float.TryParse(CommandLine["Homeo"],out tr)) {
						Homeo = true; //  set homeostatic target to a float if provided and it's valid!
					}
				}
			}

			if(CommandLine["TN"] != null){
				if (CommandLine ["TN"] == "false") {
					TN = false; 
				} else {
					TN = true;
				}
			}

			TargRate.GetComponent<Slider> ().value = tr;
			Input_Homeo.GetComponent<Toggle> ().isOn = Homeo; // force toggles to be on or off.
			Input_TN.GetComponent<Toggle> ().isOn = TN;

			// display the cameras.
			MainCamera.enabled = true;		
			FigureCamera.enabled = true;
		

			if(CommandLine["CThresh"] != null){
				if (float.TryParse(CommandLine["CThresh"],out Conn_Thresh)) {
				}
			}

			// Threshold the connectivity matrix in Cbase into C.
			SumCBase = 0;
			for (int p = 0; p < N; p++) {
				for (int q = 0; q < N; q++) {
					CBaseAdapt [p, q] = CBase [p, q];
					SumCBase = CBaseAdapt [p, q] + SumCBase;
					if (CBase [p, q] > Conn_Thresh)
						C [p, q] = 1;
					else
						C [p, q] = 0;
				}
			}
						

			// RENDER Some stuff (LHS Render)		
			for (int i = 0; i < N; i++) {
				Vector3 pos = new Vector3 (Locations [i, 0], Locations [i, 2], Locations [i, 1]); 
				GameObject clone = Instantiate (NetworkNode, pos, Quaternion.identity) as GameObject; 
				clone.name = "Node" + i.ToString ();
		
			
			} 
			int[] MotorOutputs = { 48, 56, 15, 23 };
			for (int ij = 0; ij < 4; ij++) {
					
				GameObject CurrentNode = GameObject.Find ("Node" + MotorOutputs [ij].ToString ());
				GameObject clone = Instantiate (NodeText, CurrentNode.transform.position, Quaternion.identity) as GameObject; 
				clone.name = "NodeText" + MotorOutputs [ij].ToString ();
				clone.GetComponent<TextMesh> ().text = "M+";
				clone.GetComponent<TextMesh> ().fontSize = 50;
			}
			int[] SensoryInputs = { 21, 54, 20, 10, 43, 53 };
			for (int ij = 0; ij < 6; ij++) {
					
				GameObject CurrentNode = GameObject.Find ("Node" + SensoryInputs [ij].ToString ());
				GameObject clone = Instantiate (NodeText, CurrentNode.transform.position, Quaternion.identity) as GameObject; 

				clone.GetComponent<TextMesh> ().text = "S+";
				clone.GetComponent<TextMesh> ().fontSize = 50;

				clone.name = "NodeText" + SensoryInputs [ij].ToString ();

			}
			int[] TaskNeg = { 42, 9, 55, 22 };
			for (int ij = 0; ij < 4; ij++) {
				GameObject CurrentNode = GameObject.Find ("Node" + TaskNeg [ij].ToString ());
				GameObject clone = Instantiate (NodeText, CurrentNode.transform.position, Quaternion.identity) as GameObject; 
				clone.GetComponent<TextMesh> ().text = "-ve";
				clone.name = "NodeText" + TaskNeg [ij].ToString ();
				clone.GetComponent<TextMesh> ().fontSize = 50;
			}
			// work out which lines in the brain model need to be drawn
			int val = 0;
			for (int ii = 0; ii < N; ii++) {
				for (int jj = 0; jj < N; jj++) {
					LineIndex [ii, jj] = val;
				}
			}
			// now render those lines
			Count = 0;
			for (int p = 0; p < N; p++) {
				for (int q = 0; q < N; q++) {
					if (C [p, q] > 0) {
								
						Vector3 start_pos = new Vector3 (Locations [p, 0], Locations [p, 2], Locations [p, 1]);
						Vector3 end_pos = new Vector3 (Locations [q, 0], Locations [q, 2], Locations [q, 1]);
						GameObject cloneLine = Instantiate (LineBase, start_pos, Quaternion.identity) as GameObject; 
						LineRenderer lineRenderer = cloneLine.AddComponent<LineRenderer> ();
						lineRenderer.material = new Material (Shader.Find ("Particles/Additive"));
						lineRenderer.SetColors (c1, c1);
						lineRenderer.SetWidth ((float)CBaseAdapt [p, q] * 5, (float)CBaseAdapt [p, q] * 5);
						lineRenderer.SetVertexCount (lengthOfLineRenderer);
						lineRenderer.SetPosition (0, start_pos);
						lineRenderer.SetPosition (1, end_pos);
						cloneLine.name = "Line" + Count.ToString ();
						LineIndex [p, q] = Count;
						Count++;

					}
				}
			}
			for (int r = 0; r < N; r++) {
				StatesNow [r] = 1;
			}
			for (int ii = 0; ii < N; ii++) {
				StatesPrevious [ii] = 1;
			}
			for (int iii = 0; iii < N; iii++) {
				StatesSelected [iii] = 0;
			}
				
			for (int iiii = 0; iiii < N; iiii++) {	
				ThrArray [iiii] = (float)Thr;
			}


			//open streams to these files. TODO: remove, I dont think these are particually needed...
			// Create a file to write to.
//			if (OffLineBuild) { // only try and do any output if we're doing an offline build.
//				using (StreamWriter sw = File.CreateText (SNpath)) {
//					sw.WriteLine ("");
//				}	
//				using (StreamWriter sw = File.CreateText (SSpath)) {
//					sw.WriteLine ("");
//				}	
//				using (StreamWriter sw = File.CreateText (Locpath)) {
//					sw.WriteLine ("");
//				}	
//				using (StreamWriter sw = File.CreateText (Thrpath)) {
//					sw.WriteLine ("");
//				}	
//				using (StreamWriter sw = File.CreateText (Paramspath)) {
//					sw.WriteLine ("");
//				}	
//			}
			//if we're running in batch mode, it'd be useful to say that
			// Code that runs at each frame update before the frame is rendered
			if (CommandLine ["batchmode"] != null) {
				Debug.Log ("Running in Batchmode!"); // therefore starting run without spacebar.
				ModelUpdateInterval = SpeedSlider.GetComponent<Slider> ().value = 0;
				started = true;
			}
		}

		void Update(){

			if (T > tmax) {
				Application.Quit ();
			}

			// Get most recent thresholds from the interface components.
			pQE = Input_PQE.GetComponent<Slider> ().value;
			Thr = (float)Input_Thresh.GetComponent<Slider> ().value;
			ModelUpdateInterval = SpeedSlider.GetComponent<Slider> ().value;
			Homeo = Input_Homeo.GetComponent<Toggle> ().isOn;
			if (Homeo) {
				tr = TargRate.GetComponent<Slider> ().value;
			}
			TN = Input_TN.GetComponent<Toggle> ().isOn;
			if (oldThrVal != Thr) {
				oldThrVal = Thr;
				for (int iiii = 0; iiii < N; iiii++) {

					ThrArray [iiii] = (float)Thr;
				}
			}

			// prevent update from running if we haven't passed the "press space to start"
			if (Input.GetKeyDown (KeyCode.Space) && !started) {
				Debug.Log ("Model Started Executing");
				Text TextObject = GameObject.Find ("WelcomeText").GetComponent<Text> (); // get rid of the startup text.
				TextObject.enabled=false;
				started = true;
			}

			if (Time.time - timeOld > ModelUpdateInterval && started) { // render frame only if timestep is large enough and we passed the "press space to start.
				// update the model
				for (int p = 0; p < N; p++) {

					StatesPrevious [p] = StatesNow [p];
				}

				timeOld = Time.time; // hold in memory the time that we calcualted this step (so that we could vary the delay between now and then.

				// perform actual model logic (also make some changes to the LHS render)
				for (int i = 0; i < N; i++) { // loopthough the states of all of the 66 nodes
					// Model Logic.
					if (StatesSelected [i] == 1) {
						StatesNow [i] = Excitatory;
						TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
						TempNode.material = NodeMaterialSelected;
						TempNode.material.color = Color.red;
					} else if (StatesSelected [i] == 2) {
						// make node quiescent if specifically asked to.
						StatesNow [i] = Quiescent; // Refractory Nodes become Quiesecent (p(R>Q) = pQR)
						TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
						TempNode.material = NodeMaterial;
						TempNode.material.color = Color.white;
					} else {
						if (StatesNow [i] == Excitatory) {							
							StatesNow [i] = Refractory; // Excitatory nodes ALWAYS become Refractory (p(E>R) = 1)
							TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
							TempNode.material = NodeMaterial;
							TempNode.material.color = Color.blue;
						} else if (StatesNow [i] == Refractory) {
							if (UnityEngine.Random.Range (0.0f, 1.0f) < pRQ) {
								StatesNow [i] = Quiescent; // Refractory Nodes become Quiesecent (p(R>Q) = pQR)
								TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
								TempNode.material = NodeMaterial;
								TempNode.material.color = Color.white;
							}
						} else if (StatesNow [i] == Quiescent) { 
							if (UnityEngine.Random.Range (0.0f, 1.0f) < pQE) {
								StatesNow [i] = Excitatory; // Quiesent Nodes become Excitatory (pQ>E) = pQE
								TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
								TempNode.material = NodeMaterial;
								TempNode.material.color = Color.red;
							} else { // if node didn't become Excitatory randomly, it might because of it's input though
								// Get the weight of input to the current node (Crow) 
								Crow = 0;
								for (int s = 0; s < N; s++) {
									if (C [i, s] == 1 && StatesPrevious [s] == Excitatory) {
										Crow = Crow + (float)CBaseAdapt [i, s] * Str;
									}
								}
								if (Crow > ThrArray [i]) {		
									StatesNow [i] = Excitatory; // Quiesent Nodes become Excitatory additionally if sum(Ei>i) > Thr.
									TempNode = GameObject.Find ("Node" + i.ToString ()).GetComponent<Renderer> ();
									TempNode.material.color = Color.red;
								}
							}					
						}
					}

					if (Homeo) { 
						if (StatesSelected[i] == 0) { 
						if (StatesNow[i] == Excitatory){
							StatesAv[i] = (StatesAv[i]*((HistoryLength-1.0f)/HistoryLength)) + (1/HistoryLength); // over distance of HistoryLength (ish)
						} else {
							StatesAv[i] = (StatesAv[i]*((HistoryLength-1.0f)/HistoryLength)) + 0; // over distance of HistoryLength (ish)
						}
						// makes no sense to tune weights where nodes are deliberately set to a value.
						ThrArray [i] =  ThrArray [i] + ((StatesAv [i]  - tr) * lr); // head towards the target rate ALWAYS!
						
						if (ThrArray [i] < 0.0f)
						{
							ThrArray [i] = 0.0f; // prevent threshold shrinking too far.
							}
						}
					}

				}
				// Render FC in the LHS Frame.
				for (int p = 0; p < N; p++) {
					for (int q = 0; q < N; q++) {
						if (StatesNow [p] == Excitatory && StatesNow [q] == Excitatory && C [p, q] > 0) {
							int LineNum = LineIndex [p, q];
							TempLine = GameObject.Find ("Line" + LineNum.ToString ()).GetComponent<LineRenderer> ();
							TempLine.SetColors (c3, c3);
							TempLine.SetWidth (2.5F, 2.5F);
						} else if (StatesPrevious [p] == Excitatory && StatesPrevious [q] == Excitatory) {
							int LineNum = LineIndex [p, q];
							TempLine = GameObject.Find ("Line" + LineNum.ToString ()).GetComponent<LineRenderer> ();
							TempLine.SetColors (c2, c2);
							TempLine.SetWidth ((float)CBaseAdapt [p, q] * 5, (float)CBaseAdapt [p, q] * 5);
						}
					}
				}
				T = T + 1;


				// Setup stuff for saving out
				// Pathts to output text files that are created
				SNpath = @"StatesNow.txt";
				SSpath = @"StatesSelected.txt";
				Locpath = @"Locations.txt";
				Thrpath = @"Thresholds.txt";
				Paramspath = @"Params.txt";

				if (Memmode == true)
				{
					if ((T % 1000) == 0) {
						filenumber = filenumber + 1;
					}

					SNpath = string.Concat(filenumber.ToString(), @"_StatesNow.txt");
					SSpath = string.Concat(filenumber.ToString(), @"_StatesSelected.txt");
					Locpath = string.Concat(filenumber.ToString(), @"_Locations.txt");
					Thrpath = string.Concat(filenumber.ToString(), @"_Thresholds.txt");
					Paramspath = string.Concat(filenumber.ToString(), @"_Params.txt");
				}

				if (CommandLine ["outpath"] != null) {
					SNpath = string.Concat(CommandLine ["outpath"] , SNpath);
					SSpath = string.Concat(CommandLine ["outpath"] , SSpath);
					Locpath = string.Concat(CommandLine ["outpath"] , Locpath);
					Thrpath = string.Concat(CommandLine ["outpath"] , Thrpath);
					Paramspath = string.Concat(CommandLine ["outpath"] , Paramspath);
					Debug.Log (CommandLine ["outpath"]);
				}

				// Write current timestep out to file.
				using (StreamWriter sw = File.AppendText (SSpath)) {  
					string str = "";
					for (int i = 0; i < StatesSelected.Length; i++) {
						str = str + StatesSelected [i].ToString () + " ";
					}
					sw.WriteLine (str);
				}	
				using (StreamWriter sw = File.AppendText (SNpath)) {  
					string str = "";
					for (int i = 0; i < StatesNow.Length; i++) {
						str = str + StatesNow [i].ToString () + " ";
					}
					sw.WriteLine (str);
				}
				using (StreamWriter sw = File.AppendText (Locpath)) {  
					string str = "";
					str = str + GameAvatar.transform.position.x.ToString () + " " + GameAvatar.transform.position.z.ToString () + " " + GameAvatar.GetComponent<Motor> ().h + " " + GameAvatar.GetComponent<Motor> ().v;sw.WriteLine (str);
				}
				using (StreamWriter sw = File.AppendText (Thrpath)) {  
					string str = "";	
					for (int i = 0; i < ThrArray.Length; i++) {
						str = str + ThrArray [i].ToString () + " ";
					}
					sw.WriteLine (str);
				}
				using (StreamWriter sw = File.AppendText (Paramspath)) {  
					string str = "";
					str = str + T.ToString () + " " + pQE.ToString () + " " + pRQ.ToString () + " " + Thr.ToString () + " " + tr.ToString () + " " + Homeo.ToString () + " " + TN.ToString () + " " + RandomIndices [0].ToString () + " " + RandomIndices [1].ToString () + " " + RandomIndices [2].ToString () + " " + RandomIndices [3].ToString () + " " + RandomIndices [4].ToString () + " " + RandomIndices [5].ToString () + " " + RandomIndices [6].ToString ();
					sw.WriteLine (str);	
				}
			}

			// Finally, an option to return to Kansas.
			if (Input.GetKey ("escape")) {
				Application.Quit ();
			}
		}
	}
}
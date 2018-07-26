using System.Diagnostics;
using UnityEngine;
using Thrift.Protocol;
using Thrift.Transport;
using avatar_interop;
using System.Net.Sockets;
using UnityEngine.UI;
using HelperScripts;
using Mono.Unix;
using Debug = UnityEngine.Debug;

public class AvatarInterop : MonoBehaviour
{

	private TTransport transport;
	private TProtocol protocol;
	public AvatarIO.Client client;
	public GameObject Avatar;
	public double[] States;
	public GameObject NetworkNode;
	private bool SS_R;
	private bool SS_L;
	private bool V_R;
	private bool V_L;
	public double Fwd;
	public double Rot;
    public int NextSimulation;
    public int StepSimulation = 0;

	Arguments CommandLine=new Arguments(System.Environment.GetCommandLineArgs()); // get and parse command line arguments.


	private float _maxvall = 0.0f;
	private float maxvall {
		get {
			//_maxvall = 0.0f;
			foreach (double d in States) {
				if (Mathf.Abs((float)d) > _maxvall) {
					_maxvall = Mathf.Abs((float)d);
				}
			}
			return _maxvall;
		}
	}
	public Text ExceptionText;

	// Update is called once per frame
	void Start ()
	{
        Connect();
	}

	void DrawModel ()
	{
		// Assume we're already connected, or, you know. Sadness.
		// Get the Model information from Python. All of it Dammit.
		// clear existing if exist
		GameObject[] existingnodes = GameObject.FindGameObjectsWithTag("Nodes");
		for (int i = 0; i < existingnodes.Length; i++) {
			Destroy (existingnodes [i]);
		}

		// redraw shiny new nodes.
		int N = client.GetNodeNumber();
		for (int i = 0; i < N; i++) {
			double[] tmp = client.GetNodeLocation (i).ToArray();
			Vector3 pos = new Vector3 ((float)tmp[0], (float)tmp[2], (float)tmp[1]);
			GameObject clone = Instantiate (NetworkNode, pos, Quaternion.identity) as GameObject;
			clone.name = "Node" + i.ToString ();
			clone.tag = "Nodes";
		}
	}
	void UpdateModel ()
	{
		ColorMap cm = new ColorMap (101);
		int[,] cmj = cm.Jet();
		//again, assumes that model is correctly drawn.....
		int N = client.GetNodeNumber();
		for (int i = 0; i < N; i++) {
			GameObject clone = GameObject.Find ("Node" + i.ToString ());
			int idx = (int)((States [i] / maxvall) * 100);
			Color clear = new Color ((float)cmj [idx, 1] / 255,
				(float)cmj [idx, 2] / 255,
				(float)cmj [idx, 3] / 255);
			clone.GetComponent<Renderer> ().material.SetColor ("_Color", clear);
		}
	}

	void Connect ()
	{
		try {

			if(CommandLine["port"] != null){
				// this hook, enables or disables listening, on a specific unix port, if that doesn't exist, go hunting on an alternative port!
				var unixExp = new UnixEndPoint(CommandLine["port"]);
				var skt = new Socket(AddressFamily.Unix,SocketType.Stream,ProtocolType.IP);
				skt.Connect(unixExp); // this technically opens the transport..
				var cli = new TcpClient();
				cli.Client = skt;
				transport = new TSocket(cli);
			}
				else{
				transport = new TSocket ("localhost", 9090);
				transport.Open ();
			}



			protocol = new TBinaryProtocol (transport);
			client = new AvatarIO.Client (protocol);

			ExceptionText.enabled = false;
			DrawModel();
		} catch (SocketException) {
			ExceptionText.enabled = true;
			ExceptionText.text = "No Connection!";
			Fwd = 0;
			Rot = 0;
		}


	}

	void Update ()
	{
		try {
            NextSimulation = client.NextSimulation();
			if (NextSimulation > StepSimulation) {
			    Fwd = client.GetFwd();
			    Rot = client.GetRot();
                States = client.GetStates().ToArray ();
                UpdateModel();
                // Send Avatar coordinates and signal to Python and tell it should continue the simulation
			}
        } catch (TTransportException) {
        	Connect();
        }

	}

	// Use this for initialization
	public void RewardSignal (bool Reward)
	{
		if (transport.IsOpen) {
			client.RewardSignal (Reward);
		} else {
			Connect ();
		}

	}

	public void SalienceSignal (bool Salience)
	{
		if (transport.IsOpen) {
			client.SalienceSignal (Salience);
		} else {
			Connect ();
		}

	}

	public void Somatosensory_R (bool ColRight)
	{
		if (transport.IsOpen) {
			if (ColRight != SS_R) {
				SS_R = ColRight;
				client.Somatosensory_R (ColRight);
			}
		} else {
			Connect ();
		}
	}

	public void Somatosensory_L (bool ColLeft)
	{
		if (transport.IsOpen) {
			if (ColLeft != SS_L) {
				SS_L = ColLeft;
				client.Somatosensory_L (ColLeft);
			}
		} else {
			Connect ();
		}
	}

	public void Visual_R (bool VisRight)
	{
		if (transport.IsOpen) {
			if (VisRight != V_R) {
				V_R = VisRight;
				client.Visual_R (VisRight);
			}
		} else {
			Connect ();
		}
	}

	public void Visual_L (bool VisLeft)
	{
		if (transport.IsOpen) {
			if (VisLeft != V_L) {
				V_L = VisLeft;
				client.Visual_L (VisLeft);
			}
		} else {
			Connect ();
		}
	}
}

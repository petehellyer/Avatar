using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using System.Collections.Specialized;
using System.Text.RegularExpressions;

namespace HelperScripts {

	public class IO {

		public static float[,] readCSV(string path)
		{

			TextAsset data = Resources.Load (path) as TextAsset; // use unity text assets from Resources Folder.
			// first work out the dimensions. We'll be cleverer after that.
			List<float> tmp = new List<float>();
			int xpoint = 0;
			int ypoint = 0;
			foreach (string line in data.ToString().Split(Environment.NewLine.ToCharArray())) {
				xpoint = xpoint + 1;
				if (line == "") { // very rough garbage collection. but does it need to be cleaner? Answers, Postcards, combine!
					continue;
				}
				ypoint = 0;
				foreach (string col in line.Split(",".ToCharArray())){
					tmp.Add (Convert.ToSingle (col));
					ypoint = ypoint + 1;
				}

			}
			// now reshape tmp to the right shape.
			float[,] parseddata = new float[xpoint, ypoint];
			float[] tmp2 = tmp.ToArray ();
			Buffer.BlockCopy(tmp2, 0, parseddata, 0, tmp2.Length * sizeof(float));
			return parseddata; // Finally, after all this ugly hackery, return a nicely formated Array.
		}

	}
	/// <summary>
	/// Arguments class - adapted from http://www.codeproject.com/Articles/3111/C-NET-Command-Line-Arguments-Parser
	/// </summary>
	public class Arguments{
		// Variables
		private StringDictionary Parameters;

		// Constructor
		public Arguments(string[] Args)
		{
			Parameters = new StringDictionary();
			Regex Spliter = new Regex(@"^-{1,2}|^/|=|:",
				RegexOptions.IgnoreCase|RegexOptions.Compiled);

			Regex Remover = new Regex(@"^['""]?(.*?)['""]?$",
				RegexOptions.IgnoreCase|RegexOptions.Compiled);

			string Parameter = null;
			string[] Parts;

			// Valid parameters forms:
			// {-,/,--}param{ ,=,:}((",')value(",'))
			// Examples: 
			// -param1 value1 --param2 /param3:"Test-:-work" 
			//   /param4=happy -param5 '--=nice=--'
			foreach(string Txt in Args)
			{
				// Look for new parameters (-,/ or --) and a
				// possible enclosed value (=,:)
				Parts = Spliter.Split(Txt,3);

				switch(Parts.Length){
				// Found a value (for the last parameter 
				// found (space separator))
				case 1:
					if(Parameter != null)
					{
						if(!Parameters.ContainsKey(Parameter)) 
						{
							Parts[0] = 
								Remover.Replace(Parts[0], "$1");

							Parameters.Add(Parameter, Parts[0]);
						}
						Parameter=null;
					}
					// else Error: no parameter waiting for a value (skipped)
					break;

					// Found just a parameter
				case 2:
					// The last parameter is still waiting. 
					// With no value, set it to true.
					if(Parameter!=null)
					{
						if(!Parameters.ContainsKey(Parameter)) 
							Parameters.Add(Parameter, "true");
					}
					Parameter=Parts[1];
					break;

					// Parameter with enclosed value
				case 3:
					// The last parameter is still waiting. 
					// With no value, set it to true.
					if(Parameter != null)
					{
						if(!Parameters.ContainsKey(Parameter)) 
							Parameters.Add(Parameter, "true");
					}

					Parameter = Parts[1];

					// Remove possible enclosing characters (",')
					if(!Parameters.ContainsKey(Parameter))
					{
						Parts[2] = Remover.Replace(Parts[2], "$1");
						Parameters.Add(Parameter, Parts[2]);
					}

					Parameter=null;
					break;
				}
			}
			// In case a parameter is still waiting
			if(Parameter != null)
			{
				if(!Parameters.ContainsKey(Parameter)) 
					Parameters.Add(Parameter, "true");
			}
		}

		// Retrieve a parameter value if it exists 
		// (overriding C# indexer property)
		public string this [string Param]
		{
			get
			{
				return(Parameters[Param]);
			}
		}
	}
} 
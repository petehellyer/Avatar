using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using System.Collections.Specialized;
using System.Text.RegularExpressions;

namespace HelperScripts
{


	public class ColorMap
	{
		private int colormapLength = 64;
		private int alphaValue = 255;

		public ColorMap ()
		{
		}

		public ColorMap (int colorLength)
		{
			colormapLength = colorLength;
		}

		public ColorMap (int colorLength, int alpha)
		{
			colormapLength = colorLength;
			alphaValue = alpha;
		}

		public int[,] Spring ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[] spring = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				spring [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = 255;
				cmap [i, 2] = (int)(255 * spring [i]);
				cmap [i, 3] = 255 - cmap [i, 1];
			}
			return cmap;
		}

		public int[,] Summer ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[] summer = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				summer [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = (int)(255 * summer [i]);
				cmap [i, 2] = (int)(255 * 0.5f * (1 + summer [i]));
				cmap [i, 3] = (int)(255 * 0.4f);
			}
			return cmap;
		}

		public int[,] Autumn ()
		{   
			int[,] cmap = new int[colormapLength, 4];
			float[] autumn = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				autumn [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = 255;
				cmap [i, 2] = (int)(255 * autumn [i]);
				cmap [i, 3] = 0;
			}
			return cmap;
		}

		public int[,] Winter ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[] winter = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				winter [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = 0;
				cmap [i, 2] = (int)(255 * winter [i]);
				cmap [i, 3] = (int)(255 * (1.0f - 0.5f * winter [i]));
			}
			return cmap;
		}

		public int[,] Gray ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[] gray = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				gray [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = (int)(255 * gray [i]);
				cmap [i, 2] = (int)(255 * gray [i]);
				cmap [i, 3] = (int)(255 * gray [i]);
			}
			return cmap;
		}

		public int[,] Jet ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[,] cMatrix = new float[colormapLength, 3];
			int n = (int)Math.Ceiling (colormapLength / 4.0f);
			int nMod = 0;
			float[] fArray = new float[3 * n - 1];
			int[] red = new int[fArray.Length];
			int[] green = new int[fArray.Length];
			int[] blue = new int[fArray.Length];

			if (colormapLength % 4 == 1) {
				nMod = 1;
			}

			for (int i = 0; i < fArray.Length; i++) {
				if (i < n)
					fArray [i] = (float)(i + 1) / n;
				else if (i >= n && i < 2 * n - 1)
					fArray [i] = 1.0f;
				else if (i >= 2 * n - 1)
					fArray [i] = (float)(3 * n - 1 - i) / n;
				green [i] = (int)Math.Ceiling (n / 2.0f) - nMod + i;
				red [i] = green [i] + n;
				blue [i] = green [i] - n;
			}

			int nb = 0;
			for (int i = 0; i < blue.Length; i++) {
				if (blue [i] > 0)
					nb++;
			}

			for (int i = 0; i < colormapLength; i++) {
				for (int j = 0; j < red.Length; j++) {
					if (i == red [j] && red [j] < colormapLength) {
						cMatrix [i, 0] = fArray [i - red [0]];
					}
				}
				for (int j = 0; j < green.Length; j++) {
					if (i == green [j] && green [j] < colormapLength)
						cMatrix [i, 1] = fArray [i - (int)green [0]];
				}
				for (int j = 0; j < blue.Length; j++) {
					if (i == blue [j] && blue [j] >= 0)
						cMatrix [i, 2] = fArray [fArray.Length - 1 - nb + i];
				}
			}

			for (int i = 0; i < colormapLength; i++) {
				cmap [i, 0] = alphaValue;
				for (int j = 0; j < 3; j++) {
					cmap [i, j + 1] = (int)(cMatrix [i, j] * 255);
				}
			}
			return cmap;
		}

		public int[,] Hot ()
		{
			int[,] cmap = new int[colormapLength, 4];
			int n = 3 * colormapLength / 8;
			float[] red = new float[colormapLength];
			float[] green = new float[colormapLength];
			float[] blue = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				if (i < n)
					red [i] = 1.0f * (i + 1) / n;
				else
					red [i] = 1.0f;
				if (i < n)
					green [i] = 0f;
				else if (i >= n && i < 2 * n)
					green [i] = 1.0f * (i + 1 - n) / n;
				else
					green [i] = 1f;
				if (i < 2 * n)
					blue [i] = 0f;
				else
					blue [i] = 1.0f * (i + 1 - 2 * n) / (colormapLength - 2 * n);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = (int)(255 * red [i]);
				cmap [i, 2] = (int)(255 * green [i]);
				cmap [i, 3] = (int)(255 * blue [i]);
			}
			return cmap;
		}

		public int[,] Cool ()
		{
			int[,] cmap = new int[colormapLength, 4];
			float[] cool = new float[colormapLength];
			for (int i = 0; i < colormapLength; i++) {
				cool [i] = 1.0f * i / (colormapLength - 1);
				cmap [i, 0] = alphaValue;
				cmap [i, 1] = (int)(255 * cool [i]);
				cmap [i, 2] = (int)(255 * (1 - cool [i]));
				cmap [i, 3] = 255;
			}
			return cmap;
		}
	}


	public class IO
	{

		public static float[,] readCSV (string path)
		{

			TextAsset data = Resources.Load (path) as TextAsset; // use unity text assets from Resources Folder.
			// first work out the dimensions. We'll be cleverer after that.
			List<float> tmp = new List<float> ();
			int xpoint = 0;
			int ypoint = 0;
			foreach (string line in data.ToString().Split(Environment.NewLine.ToCharArray())) {
				xpoint = xpoint + 1;
				if (line == "") { // very rough garbage collection. but does it need to be cleaner? Answers, Postcards, combine!
					continue;
				}
				ypoint = 0;
				foreach (string col in line.Split(",".ToCharArray())) {
					tmp.Add (Convert.ToSingle (col));
					ypoint = ypoint + 1;
				}

			}
			// now reshape tmp to the right shape.
			float[,] parseddata = new float[xpoint, ypoint];
			float[] tmp2 = tmp.ToArray ();
			Buffer.BlockCopy (tmp2, 0, parseddata, 0, tmp2.Length * sizeof(float));
			return parseddata; // Finally, after all this ugly hackery, return a nicely formated Array.
		}

	}

	/// <summary>
	/// Arguments class - adapted from http://www.codeproject.com/Articles/3111/C-NET-Command-Line-Arguments-Parser
	/// </summary>
	public class Arguments
	{
		// Variables
		private StringDictionary Parameters;

		// Constructor
		public Arguments (string[] Args)
		{
			Parameters = new StringDictionary ();
			Regex Spliter = new Regex (@"^-{1,2}|^/|=|:",
				                RegexOptions.IgnoreCase | RegexOptions.Compiled);

			Regex Remover = new Regex (@"^['""]?(.*?)['""]?$",
				                RegexOptions.IgnoreCase | RegexOptions.Compiled);

			string Parameter = null;
			string[] Parts;

			// Valid parameters forms:
			// {-,/,--}param{ ,=,:}((",')value(",'))
			// Examples: 
			// -param1 value1 --param2 /param3:"Test-:-work" 
			//   /param4=happy -param5 '--=nice=--'
			foreach (string Txt in Args) {
				// Look for new parameters (-,/ or --) and a
				// possible enclosed value (=,:)
				Parts = Spliter.Split (Txt, 3);

				switch (Parts.Length) {
				// Found a value (for the last parameter 
				// found (space separator))
				case 1:
					if (Parameter != null) {
						if (!Parameters.ContainsKey (Parameter)) {
							Parts [0] = 
								Remover.Replace (Parts [0], "$1");

							Parameters.Add (Parameter, Parts [0]);
						}
						Parameter = null;
					}
					// else Error: no parameter waiting for a value (skipped)
					break;

				// Found just a parameter
				case 2:
					// The last parameter is still waiting. 
					// With no value, set it to true.
					if (Parameter != null) {
						if (!Parameters.ContainsKey (Parameter))
							Parameters.Add (Parameter, "true");
					}
					Parameter = Parts [1];
					break;

				// Parameter with enclosed value
				case 3:
					// The last parameter is still waiting. 
					// With no value, set it to true.
					if (Parameter != null) {
						if (!Parameters.ContainsKey (Parameter))
							Parameters.Add (Parameter, "true");
					}

					Parameter = Parts [1];

					// Remove possible enclosing characters (",')
					if (!Parameters.ContainsKey (Parameter)) {
						Parts [2] = Remover.Replace (Parts [2], "$1");
						Parameters.Add (Parameter, Parts [2]);
					}

					Parameter = null;
					break;
				}
			}
			// In case a parameter is still waiting
			if (Parameter != null) {
				if (!Parameters.ContainsKey (Parameter))
					Parameters.Add (Parameter, "true");
			}
		}

		// Retrieve a parameter value if it exists
		// (overriding C# indexer property)
		public string this [string Param] {
			get {
				return(Parameters [Param]);
			}
		}
	}
} 
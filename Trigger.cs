using PuppetMasterKit.Utility.Noise;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ConsoleUnitTest
{
  class Program
  {
    static float[,] grad = { 
        { 0.2f, -0.6f, 0.9f, 0.2f, -0.4f,},
        { 0.2f, 1f, 0.2f, 0.2f, 0.4f,},
        { -0.2f, 1f, -0.9f, -0.2f, 0.9f,},
        { 0.3f, 0.6f, -0.7f, 0.2f, 0.2f,},
        { 0.2f, 0.1f, 0.3f, -0.1f, 0.1f,},
      };

    static Color[] biome = {Color.Blue, Color.Brown, Color.Green, Color.Gray, Color.White};

    static float[,] GenerateGradient(int n){ 
      var res = new float[n,n];
      var random = new Random(1);
      for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
          res[i,j]=(50-random.Next(100))/100f;

        }
      }
      return res;
    }

    static Tuple<float,float> GetValueRange(int colorIndex){ 
      var interval = 2f/biome.Length;
      return Tuple.Create(-1+interval*colorIndex, -1+interval*colorIndex + interval);
    }

    static Color FromPerlin(double val){ 
      var n = biome.Length;
      if(val==1)
        return biome[biome.Length-1];
      var sel = (int)(((val +1)/2)*n);
      //ControlPaint.Light(Color.Red,;
      return biome[sel];
    }
    
    static void Main(string[] args){ 
      var mapper = new IsometricMapper();
      var gradient = GenerateGradient(30);
      var perlin = new Perlin(gradient);
      var amplitude = 2.3f;
      var frq = 10f;
      var tileW = 128;
      var tileH = 64;
      var w = tileW * 15;
      var h = tileH * 15;
      var org = new PuppetMasterKit.Graphics.Geometry.Point(w/2-1,h/2-1+64/2);
      var mid = GetValueRange((int)Math.Round(biome.Length/2f));
      var dim = 5 * tileW;
      using (Bitmap b = new Bitmap(w, h)) {
      using (Graphics g = Graphics.FromImage(b)) {

          for (float i = 0; i < dim; i++) {
            for (float j = 0; j < dim; j++) {
              var p = mapper.ToScene(new PuppetMasterKit.Graphics.Geometry.Point(i,j)) + org;
              var gx = i/dim;
              var gy = j/dim;
              var pn = 10 * perlin.Noise(frq*gx,frq*gy)
                //+ 3.5 * perlin.Noise(2*frq*gx,2*frq*gy)
                //+ 0.1 * perlin.Noise(4*frq*gx,4*frq*gy)
                ;// * amplitude;
              var gd = PuppetMasterKit.Graphics.Geometry.Point.Distance(new PuppetMasterKit.Graphics.Geometry.Point(i,j), new PuppetMasterKit.Graphics.Geometry.Point(dim/2, dim/2));
              var td = PuppetMasterKit.Graphics.Geometry.Point.Distance(new PuppetMasterKit.Graphics.Geometry.Point(0,0), new PuppetMasterKit.Graphics.Geometry.Point(dim/2, dim/2));
              var d = gd/td;
              pn = (1+pn-d)/2;

              pn = pn < 0?0:(pn>1?1:pn);
              p.Y -= (float)pn * 70f;
              
              var color = FromPerlin(pn);
              //b.SetPixel((int)Math.Round(p.X),(int)Math.Round(p.Y+1),color);
              //b.SetPixel((int)Math.Round(p.X),(int)Math.Round(p.Y+0.5),color);
              b.SetPixel((int)Math.Round(p.X),(int)Math.Round(p.Y),color);
              //g.DrawLine(new Pen(color), (float)p.X, (float)p.Y, (float)p.X, (float)(p.Y +1));
            }
          }
      }
      b.Save(@"C:\Temp\dd\green.png", ImageFormat.Png);
    }
    }
  }
}

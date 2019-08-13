using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PmColor = PuppetMasterKit.Utility.Color;

namespace ConsoleUnitTest
{
  class Program
  {
    static void Main(string[] args) 
      { 
      var tileSize = 128;
      var tileCount = 5;
      var colors = new PmColor[] { //new PmColor(0xAF,0xEE,0xEE, 0xFF), 
        new PmColor(0xFF,0xFF,0xFF, 0x00), 
        new PmColor(0xc2,0xb2,0x80, 0xFF), 
        new PmColor(0x99,0xe6,0x00, 0xFF), 
        new PmColor(0x00,0xcc,0x00, 0xFF), 
        new PmColor(0x80,0x80,0x80, 0xFF), 
        new PmColor(0xFF,0xFF,0xFF, 0xFF), };

      var intervals = new float[] { 0.05f, 0.2f, 0.35f, 0.45f, 0.70f, 1f };
      
      using (Bitmap b = new Bitmap(tileSize*tileCount, tileSize*tileCount)) {
        using (Graphics g = Graphics.FromImage(b)) {
          g.CompositingQuality = CompositingQuality.HighQuality;
          g.PixelOffsetMode = PixelOffsetMode.HighQuality;    
          var generator = new MountainGenerator.MountainGeneratorBuilder()
            .WithColorRange(colors, intervals)
            .WithMapper(new IsometricMapper())
            .WithSeed(199)
            .WithGradient(300)
            .WithMaxFrequency(9)
            .WithTileSize(tileSize)
            .WithTileCount(tileCount)
            .WithHeight(100f)
            .WithDrawingFunction((x,y,color)=>{ 
              b.SetPixel((int)x, (int)y, 
                Color.FromArgb((int)color.Alpha, (int)color.Red, (int)color.Green, (int)color.Blue) );
             })
            .Build();
            generator.Paint();
        }
        b.Save(@"C:\Temp\dd\new-map.png", ImageFormat.Png);
      }
      Console.WriteLine("Done.");
      Console.ReadKey();
    }
  }
}

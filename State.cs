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
      var colors = new PmColor[] { //new PmColor(0xE0,0xFF,0xFF, 0xFF), 
        new PmColor(0xAB,0xE0,0xF8, 0xFF),
        new PmColor(0xC7,0xEA,0xFA, 0xFF), //c7eafa
        new PmColor(0xc2,0xb2,0x80, 0xFF), 
        new PmColor(0x99,0xe6,0x00, 0xFF), 
        new PmColor(0x00,0xcc,0x00, 0xFF), 
        new PmColor(0x80,0x80,0x80, 0xFF), 
        new PmColor(0xFF,0xFF,0xFF, 0xFF), };

      var intervals = new float[] { 0.009f, 0.03f, 0.034f, 0.38f, 0.45f, 0.60f, 1f };
      
      var start = DateTime.Now;
      using (Bitmap b = new Bitmap(tileSize*tileCount, tileSize*tileCount)) {
        using (Graphics g = Graphics.FromImage(b)) {
          g.CompositingQuality = CompositingQuality.HighQuality;
          g.PixelOffsetMode = PixelOffsetMode.HighQuality;    
          var generator = new MountainGenerator.MountainGeneratorBuilder()
            .WithColorRange(colors, intervals)
            .WithMapper(new IsometricMapper())
            .RandomSeed(21)
            .PerlinGradient(300)
            .TileSize(tileSize)
            .TileCount(tileCount)
            .MapHeight(85f)
            .MaxTerrainAmplitude(7)
            .MaxTerrainFrequency(9)
            .LightFrequency(180)
            .WaterFrequency(4)
            .DrawingFunction((x,y,color)=>{ 
              b.SetPixel((int)x, (int)y, 
                Color.FromArgb((int)color.Alpha, (int)color.Red, (int)color.Green, (int)color.Blue) );
             })
            .Build();
            generator.Paint();
        }
        b.Save(@"C:\Temp\dd\new-map.png", ImageFormat.Png);
      }
      var end = DateTime.Now;
      Console.WriteLine($"Done in {(end-start).TotalSeconds}s.");
      Console.ReadKey();
    }
  }
}

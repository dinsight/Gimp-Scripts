using PuppetMasterKit.Utility;
using PuppetMasterKit.Utility.Noise;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Point=PuppetMasterKit.Graphics.Geometry.Point;

namespace ConsoleUnitTest
{
  class MountainGenerator
  {
    public float maxHeight;
    public int gradientSize;
    public int tileSize;
    public int tileCount;
    private IsometricMapper mapper;
    private int imageSize;
    private int randomSeed;
    private Perlin landscapeTexture;
    private Perlin lightTexture;
    private Perlin waterTexture;
    private float lightTextureFrq;
    private float waterTextureFrq;
    private Color[] colors;
    private float[] intervals;
    private float maxFrequency;
    private Point origin;
    private Action<float, float, Color> draw;

    public int ImageSize { get => imageSize; }

    private MountainGenerator() {
    }

    public class MountainGeneratorBuilder
    {

      private int randomSeed;
      private float height;
      private float maxFrequency;
      private int gradSize;
      private int tileSize;
      private int tileCount;
      private Color[] colors;
      private float[] intervals;
      private IsometricMapper mapper;
      private Action<float, float, Color> draw;

      public MountainGeneratorBuilder WithMapper(IsometricMapper mapper) {
        this.mapper = mapper;
        return this;
      }

      public MountainGeneratorBuilder WithHeight(float height) {
        this.height = height;
        return this;
      }
      public MountainGeneratorBuilder WithGradient(int gradSize) {
        this.gradSize = gradSize;
        return this;
      }
      public MountainGeneratorBuilder WithTileSize(int tileSize) {
        this.tileSize = tileSize;
        return this;
      }
      public MountainGeneratorBuilder WithTileCount(int tileCount) {
        this.tileCount = tileCount;
        return this;
      }
      public MountainGeneratorBuilder WithMaxFrequency(float maxFrequency) {
        this.maxFrequency = maxFrequency;
        return this;
      }
      public MountainGeneratorBuilder WithSeed(int seed) {
        this.randomSeed = seed;
        return this;
      }
      public MountainGeneratorBuilder WithDrawingFunction(Action<float,float,Color> draw) {
        this.draw = draw;
        return this;
      }
      public MountainGeneratorBuilder WithColorRange(Color[] colors, float[] intervals) {
        this.colors = colors;
        this.intervals = intervals;
        return this;
      }

      public MountainGenerator Build() {
        var terrain = new MountainGenerator();
        terrain.draw = draw;
        terrain.maxHeight = height;
        terrain.gradientSize = gradSize;
        terrain.tileSize = tileSize;
        terrain.tileCount = tileCount;
        terrain.imageSize = tileCount * tileSize;
        terrain.lightTextureFrq = 130f / terrain.ImageSize;
        terrain.waterTextureFrq = 5f / terrain.ImageSize;
        terrain.randomSeed = randomSeed;
        terrain.colors = colors;
        terrain.intervals = intervals;
        terrain.mapper = mapper;
        terrain.maxFrequency = maxFrequency;
        var grad = terrain.GenerateGradient(gradSize);
        terrain.landscapeTexture = new Perlin(grad);
        terrain.lightTexture = terrain.landscapeTexture;//use the same noise
        terrain.waterTexture = terrain.landscapeTexture;//use the same noise
        terrain.origin = new Point(terrain.ImageSize / 2 - 1, terrain.ImageSize / 2 - 1 );
        return terrain;
      }
    }

    private float[,] GenerateGradient(int n) {
      var res = new float[n, n];
      var random = new Random(randomSeed);
      for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
          res[i, j] = (50 - random.Next(100)) / 100f;

        }
      }
      return res;
    }

    Color FromPerlin(float val, float i, float j) {

      var brightness = lightTexture.Noise(lightTextureFrq * i, lightTextureFrq * j);
      var water = waterTexture.Noise(waterTextureFrq * i, waterTextureFrq * j);
      var topVal = intervals.Where(x => x >= val).FirstOrDefault();
      var topLimIndex = intervals.ToList().IndexOf(topVal);
      var topvalue = intervals[topLimIndex];
      var bottomValue = topLimIndex == 0 ? 0 : intervals[topLimIndex - 1];
      var colorEnd = colors[topLimIndex];
      var colorStart = topLimIndex == 0 ? colors[0] : colors[topLimIndex - 1];

      var color = Blend(colorStart, colorEnd, 1 - (float)(val - bottomValue) / (topvalue - bottomValue));
      if (brightness > 0 && val > 0.1)
        return Brightness(color, 1 - brightness);

      if (water > 0 && val <= 0.1)
        return Brightness(color, 1 - water);
      return color;
    }

    private Color Blend(Color color, Color backColor, double amount) {
      byte r = (byte)((color.Red * amount) + backColor.Red * (1 - amount));
      byte g = (byte)((color.Green * amount) + backColor.Green * (1 - amount));
      byte b = (byte)((color.Blue * amount) + backColor.Blue * (1 - amount));
      return new Color(r, g, b, 0xFF);
    }

    private Color Brightness(Color color, double amount) {
      byte r = (byte)(color.Red * amount);
      byte g = (byte)(color.Green * amount);
      byte b = (byte)(color.Blue * amount);
      return new Color(r, g, b, 0xFF);
    }
    private float GetHeight(float i, float j) {
      var gx = i / ImageSize;
      var gy = j / ImageSize;
      var pn = 9 * landscapeTexture.Noise(1.2f * maxFrequency * gx, 1.2f * maxFrequency * gy)
        + 1.2 * landscapeTexture.Noise(5 * maxFrequency * gx, 5 * maxFrequency * gy)
        //+ 1.2 * perlin.Noise(2 * frq * gx, 2 * frq * gy)
        ;// * amplitude;
      var gd = Point.Distance(new Point(i, j), new Point(ImageSize / 2, ImageSize / 2));
      var td = Point.Distance(new Point(0, ImageSize / 2), new Point(ImageSize / 2, ImageSize / 2));
      var d = gd / td;
      d = d > 1 ? 1 : d;
      pn = (1 - d) * pn;
      pn = pn < 0 ? 0 : (pn > 1 ? 1 : pn);
      return (float)pn;
    }

    private Point ToSceneCoord(float i, float j) {
      var p = mapper.ToScene(new Point(i, j));
      p.Y = origin.Y - p.Y;
      p.X += origin.X;
      return p;
    }

    private void Paint(float i, float j) {
      double pn1 = GetHeight(i, j);
      Point p1 = ToSceneCoord(i, j);
      var h1 = (float)pn1 * maxHeight;
      var color1 = FromPerlin((float)pn1, i, j);

      if(p1.X >=0 && p1.Y >=0 && p1.X < ImageSize && p1.Y < ImageSize)
        draw(p1.X, p1.Y - h1, color1);

      if(i+1<ImageSize && j+1<ImageSize){ 
        double pn2 = GetHeight(i+1, j+1);
        var p2 = ToSceneCoord(i+1, j+1);
        var h2 = (float)pn2 * maxHeight;
        var y1 = (int)(p1.Y - h1);
        var y2 = (int)(p2.Y - h2);
        if (y2-y1>0) {
          var hStep = 1f / (2*(y2 - y1));
          for (float s = 0; s <= 1; s += hStep) {
            double ps = GetHeight(i + s, j + s);
            var pts = ToSceneCoord(i + s, j + s);
            var hs = (float)ps * maxHeight;
            var colorS = FromPerlin((float)ps, i + s, j + s);
            draw(pts.X, pts.Y - hs, colorS);
          }
        }
      }
    }

    public void Paint(){
      float stepX = 1;
      float stepY = 1;
      for (float i = 0; i < ImageSize; i+=stepX) {
        for (float j = 0; j < ImageSize; j+=stepY) {
          Paint(i, j);
        }
      }
    }
  }
}

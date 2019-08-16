using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using PuppetMasterKit.Utility.Extensions;
using PuppetMasterKit.Utility;
using PuppetMasterKit.Graphics.Geometry;

namespace ConsoleUnitTest.Generators.Tree
{
  class TreeGenerator
  {
    int[,] grid;
    int rows;
    int cols;

    private class Context {
      public GridCoord Coord { get; set; }
      public Vector Dir { get; set; }
      public Context(int row, int col, Vector dir) {
        Dir = dir;
        Coord = new GridCoord(row,col);
      }
    }
    
    public static void Main(){ 
      var program = new TreeGenerator();
      var code = program.Generate(3);
      program.WriteToGrid(code, 0, program.cols/2);
      program.Print();
      Console.ReadKey();
    }

    public TreeGenerator() {
      grid = new int[40,40];
      rows = grid.GetLength(0);
      cols = grid.GetLength(1);
      grid.Reset(0);
    }

    private void Print(){
      for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
          if(grid[i,j]==0){ 
            Console.Write('.');
          } else { 
            Console.Write((char)grid[i,j]);
          }
        }
        Console.WriteLine();
      }
    }

    private void WriteToGrid(String code, int startRow, int startCol){
      var context = new Stack<Context>();
      var row = startRow;
      var col = startCol;
      var vec = new Vector(0,1);
      for (int i = 0; i < code.Length; i++) {
        var ch = code[i];
        if(ch=='['){ 
          context.Push(new Context(row, col, vec));
          continue;
        } else if (ch==']'){ 
          var ctx = context.Pop();
          row = ctx.Coord.Row;
          col = ctx.Coord.Col;
          vec = ctx.Dir;
          continue;
        }
        if(ch=='F'){ 
          row = (int)Math.Round(row + vec.Dy);
          col = (int)Math.Round(col + vec.Dx);
          if(row>=0 && row<rows && col>=0 && col<cols)
            grid[row,col]='F';
        }
        if(ch=='-'){ //left 25deg
          var newAngle = GetAngle(vec)+Math.PI/6;
          vec.SetAngle((float)newAngle);
        }
        if(ch=='+'){ //right 25deg
          var newAngle = GetAngle(vec)-Math.PI/6;
          vec.SetAngle((float)newAngle);
        }
      }
    }

    public float GetAngle(Vector vector)
    {
      var len = vector.Magnitude();
      var angle = Math.Acos(vector.Dx/len );
      return (float)angle;
    }

    private String Generate(int steps) {
      var rules = new Dictionary<char, Func<string>>{ 
        {'X',()=>"F+[[X]-X]-F[-FX]+X" },
        {'F',()=>"FF" },
      };
      var buffer = new StringBuilder("FX");
      for (int i = 0; i < steps; i++) {
        var temp = new StringBuilder();
        foreach (var ch in buffer.ToString()) {
          if(rules.ContainsKey(ch))
            temp.Append(rules[ch]());
          else
            temp.Append(ch);
        }
        buffer.Clear();
        var x = temp.ToString();
        buffer.Append(x);
      }
      return buffer.ToString();
    }
  }
}

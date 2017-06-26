package spark.perf

import java.util.Random

/**
  * Created by giovanniquattrocchi on 26/06/17.
  */

class ZipfGenerator(val size: Int, val skew: Int, val seed: Int) {

  val rnd = new Random(seed)
  val harmonic: Double = (1 to size).foldLeft(0d)((a, b) => a + (1.0d / Math.pow(b, skew)))

  def next() : Int = {
    var rank: Int = rnd.nextInt(size) + 1
    var frequency: Double = (1.0d / Math.pow (rank, skew) ) / harmonic
    var dice = rnd.nextDouble()

    while (!(dice < frequency)) {
      rank = rnd.nextInt (size) + 1
      frequency = (1.0d / Math.pow (rank, skew) ) / harmonic
      dice = rnd.nextDouble()
    }
    rank
  }


  def getProbability(rank: Int): Double = {
    (1.0d / Math.pow (rank, skew) ) / harmonic
  }

}
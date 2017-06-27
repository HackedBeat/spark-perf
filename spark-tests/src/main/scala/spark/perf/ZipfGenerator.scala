package spark.perf

import java.util.Random

import com.sun.crypto.provider.AESCipher.AES128_CBC_NoPadding

/**
  * Created by giovanniquattrocchi on 26/06/17.
  */

class ZipfGenerator(val size: Int, val skew: Int, val seed: Int) {

  val rnd = new Random(seed)
  val harmonic: Double = (1 to size).foldLeft(0d)((a, b) => a + (1.0d / Math.pow(b, skew)))

  def next() : Int = {

    var rank: Int = 0
    var p, dice: Double = 0

    do {
      rank = rnd.nextInt(size) + 1
      p = getProbability(rank)
      dice = rnd.nextDouble()
    }
    while (dice >= p)

    rank
  }


  def getProbability(rank: Int): Double = {
    (1.0d / Math.pow (rank, skew) ) / harmonic
  }

}
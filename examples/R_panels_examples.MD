### Examples of R panel scripts
* An example R panel script that draws histograms of two samples using custom colors (Serge Mazères, IPBS, Toulouse)
```
data1 = rnorm(10000, -10, 10)
data2 = rnorm(10000, 10, 10)
data = data.frame("serie1" = data1, "serie2" = data2)
par(mar = c(6, 7, 5, 3))
par(mgp = c(4, 1, 0))
par(cex.main = 4, cex.lab = 3, cex.axis =2)
hist(data[,1], breaks="FD", col = rgb(0, 0, 255, 128, max = 255), main = "Test Histogram", xlim = c(- 60, 60), xlab = "Data")
hist(data[,2], breaks="FD", col = rgb(255, 0, 0, 128, max = 255), add = TRUE)
```

![image](https://user-images.githubusercontent.com/711344/123813087-e5906f00-d8f4-11eb-93fd-a67510b99c80.png)

# App-level R8 rules. JNI rules live in core/local/consumer-rules.pro.

# pdfbox-android references an optional JPEG 2000 codec that is not shipped.
-dontwarn com.gemalto.jp2.**

# Keep readable stack traces in user-submitted bug reports.
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

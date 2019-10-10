import java.io.*;
import java.util.ArrayList;

//extract useful information from project output, then combine then together and test the accuracy result.

public class extractUtils {
    public static ArrayList<String> arr;
    public static void main(String[] args) {
        arr = new ArrayList<>();
        arr.add("scientificName");
        //read test files
        for (int i = 1; i <= 20; i++) {
            try {
                BufferedReader reader = new BufferedReader(new FileReader("./Test file sample/" + i + ".csv"));
                reader.readLine();
                String line = null;
                while ((line = reader.readLine()) != null) {
                    String item[] = line.split("，");

                    String last = item[item.length - 1];

                    String[] getName = last.split(",");

                    arr.add(getName[2]);

                    //System.out.println(last);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        System.out.println(arr);
        System.out.println(arr.size());

        //extract scientific name in test files and combine them in a new file called output.csv
        try {
            File csv = new File("./Test file sample/output.csv");
            BufferedWriter writer = new BufferedWriter(new FileWriter(csv, true));
            for (int i = 0; i < arr.size(); i++) {
                writer.write(arr.get(i));
                writer.newLine();
            }
            writer.close();
        }catch (Exception e){
            e.printStackTrace();
        }
    }

}

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;

/**
 * URLs: "https://biodiversity.org.au/nsl/services/APC"; "https://biodiversity.org.au/nsl/services/APNI";
 */

public class spider {
    public static String link = "https://biodiversity.org.au/nsl/services/APNI";

    public static ArrayList<String> allInfo = new ArrayList<>();// store all information in the website (not analysis)

    public static String searchBox = "";

    public static int sbIndex = 0;

    public static String outputNo = ""; //depends on key word "panel panel-info" (include head and body)

    public static int outputNoIndex = 0; // the number of return results

    public static String output = ""; // return detail

    public static int outputIndex = 0;

    /**
     * connect the the target search engine (https://biodiversity.org.au/nsl/services/APNI)
     * @param destination
     * @throws IOException
     */
    public static void getConnect(String destination) throws IOException {

        HttpURLConnection connection = null;
        URL url = null;
        InputStream in = null;
        BufferedReader reader = null;
        StringBuffer stringBuffer = null;

        try {
            url = new URL(destination);

            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setDoInput(true);
            connection.connect();

            in = connection.getInputStream();
            reader = new BufferedReader(new InputStreamReader(in));
            stringBuffer = new StringBuffer();
            String line = null;

            while ((line = reader.readLine()) != null){
                stringBuffer.append(line);
                allInfo.add(line);
                System.out.println(line);
            }
        }catch (Exception e){
            e.printStackTrace();
        }finally {
            connection.disconnect();

            try{
                in.close();
                reader.close();
            }catch (Exception e){
                e.printStackTrace();
            }
        }

        //String rtn = stringBuffer.toString();
        //System.out.println(rtn);
        //return rtn;
    }

    /**
     * find search box and output index
     */
    public static void find(){

        for (String x: allInfo) {

            if (x.contains("Enter a name")){
                searchBox = x;
                sbIndex = allInfo.indexOf(x);
            }

            if (x.contains("class=\"panel-heading\"")){
                outputNo = x;//now get the output start position, find the end symbol (</div>) to get the full output
                outputNoIndex = allInfo.indexOf(x);
            }

            if (x.contains("class=\"panel-body\"")){
                output = x;
                outputNoIndex = allInfo.indexOf(x);
            }
        }
    }

    /**
     * find the search box and output range (get all required information)
     */
    public static void infoRange(){

        int sbEnd = 0;

        for (int i = sbIndex; i < allInfo.size(); i++) {

            if (allInfo.get(i).contains("/>")){
                sbEnd = i;
                break;
            }
        }

        for (int i = outputIndex; i < allInfo.size(); i++) {

        }
    }

    /**
     * analysis the output and delete HTML tags
     */
    public static void parser(){

    }

    public static void main(String[] args) throws IOException {

        URL url = new URL(link);
        getConnect(link);
        find();
        //for (String x: allInfo) System.out.println(x);
        System.out.println(searchBox);
        System.out.println(output);
        System.out.println(allInfo.size());
        System.out.println(sbIndex);
    }
}

// src/QueryConsole.java
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.*;
import java.sql.*;
import java.util.LinkedHashMap;
import java.util.Map;

public class QueryConsole extends JFrame {
    private JComboBox<String> combo;
    private JTextArea customArea;
    private JButton runBtn;
    private JTable resultTable;
    private DefaultTableModel tableModel;
    private Map<String,String> queries = new LinkedHashMap<>();

    public QueryConsole() {
        super("XYZCOMPANY SQL Console");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(800,600);
        setLayout(new BorderLayout());

        JPanel top = new JPanel(new BorderLayout(5,5));
        combo = new JComboBox<>();
        runBtn = new JButton("Run");
        top.add(combo, BorderLayout.CENTER);
        top.add(runBtn, BorderLayout.EAST);

        customArea = new JTextArea(3,60);
        customArea.setEnabled(false);
        JScrollPane customScroll = new JScrollPane(customArea,
            JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED,
            JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);

        tableModel = new DefaultTableModel();
        resultTable = new JTable(tableModel);
        JScrollPane tableScroll = new JScrollPane(resultTable);

        add(top, BorderLayout.NORTH);
        add(customScroll, BorderLayout.SOUTH);
        add(tableScroll, BorderLayout.CENTER);

        try (Connection conn = getConnection()) {
            DatabaseMetaData md = conn.getMetaData();
            try (ResultSet rs = md.getTables(null, null, "%", new String[]{"TABLE"})) {
                while (rs.next()) {
                    String table = rs.getString("TABLE_NAME");
                    String label = "SELECT * FROM " + table;
                    queries.put(label, label);
                }
            }
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(this, "Error fetching tables:\n"+e);
        }

        //Q1
        queries.put("Q1: INTERVIEWERS FOR HELLEN COLE ON JOB 11111",
            "SELECT DISTINCT IV.INTERVIEWER_ID, CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS INTERVIEWER_NAME\n" +
            "FROM INTERVIEW I\n" +
            " JOIN INTERVIEWER IV ON I.INTERVIEWER_ID=IV.INTERVIEWER_ID\n" +
            " JOIN EMPLOYEE E ON IV.EMPLOYEE_ID=E.EMPLOYEE_ID\n" +
            " JOIN PERSON P ON E.EMPLOYEE_ID=P.PERSONAL_ID\n" +
            " JOIN SELECTED_FOR_INTERVIEW SEL ON I.CANDIDATE_ID=SEL.SELECTED_APPLICANT\n" +
            " JOIN APPLICANT A ON SEL.APPLICANT_ID=A.APPLICANT_ID\n" +
            " JOIN PERSON PER2 ON COALESCE(A.EMPLOYEE_ID,A.POTENTIAL_EMPLOYEE_ID)=PER2.PERSONAL_ID\n" +
            "WHERE PER2.FIRST_NAME='HELLEN' AND PER2.LAST_NAME='COLE'\n" +
            "  AND SEL.JOB_ID=11111 AND I.JOB_POSITION=11111");
        // Q2
        queries.put(
            "Q2: MARKETING JOBS IN JAN 2011",
            "SELECT J.JOB_ID\n" +
            "FROM JOB J\n" +
            " JOIN DEPARTMENT D ON J.DEPARTMENT_POST = D.DEPARTMENT_ID\n" +
            "WHERE D.DEPARTMENT_NAME = 'MARKETING'\n" +
            "  AND J.POSTED_DATE BETWEEN '2011-01-01' AND '2011-01-31';"
        );


            // Q3
        queries.put("Q3: EMPLOYEES WHO SUPERVISE NOBODY",
            "SELECT E.EMPLOYEE_ID, CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS EMPLOYEE_NAME\n" +
            "  FROM EMPLOYEE E\n" +
            "  JOIN PERSON P ON E.EMPLOYEE_ID=P.PERSONAL_ID\n" +
            "  LEFT JOIN EMPLOYEE S ON E.EMPLOYEE_ID=S.EMPLOYEE_SUPERVISOR\n" +
            " WHERE S.EMPLOYEE_ID IS NULL;"
        );

        // Q4
        queries.put("Q4: MARKETING SITES WITH NO SALES IN MARCH 2011",
            "SELECT MS.SITE_ID, MS.SITE_LOCATION\n" +
            "  FROM MARKETING_SITE MS\n" +
            "  LEFT JOIN SALE S ON MS.SITE_ID=S.SITE_ID\n" +
            "    AND S.SALES_TIME BETWEEN '2011-03-01' AND '2011-03-31'\n" +
            " WHERE S.SALE_ID IS NULL;"
        );

        // Q5
        queries.put("Q5: JOBS WITH NO HIRES ONE MONTH AFTER POSTING",
            "SELECT J.JOB_ID, J.JOB_DESCRIPTION\n" +
            "  FROM JOB J\n" +
            "  LEFT JOIN Selected_Interviewees SI ON SI.JOB_ID=J.JOB_ID\n" +
            " WHERE SI.JOB_ID IS NULL\n" +
            "   AND J.POSTED_DATE <= DATE_SUB(CURDATE(), INTERVAL 1 MONTH);"
        );

        // Q6
        queries.put("Q6: SALESMEN WHO SOLD ALL PRODUCTS > $200",
            "SELECT E.EMPLOYEE_ID, CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS SALESMAN_NAME\n" +
            "  FROM SALE S\n" +
            "  JOIN EMPLOYEE E ON S.SALESMAN_ID=E.EMPLOYEE_ID\n" +
            "  JOIN PERSON P   ON E.EMPLOYEE_ID=P.PERSONAL_ID\n" +
            "  JOIN PRODUCT PR ON S.PRODUCT_ID=PR.PRODUCT_ID\n" +
            " WHERE PR.PRODUCT_LIST_PRICE>200\n" +
            " GROUP BY E.EMPLOYEE_ID\n" +
            "HAVING COUNT(DISTINCT PR.PRODUCT_TYPE)=(\n" +
            "    SELECT COUNT(DISTINCT PRODUCT_TYPE)\n" +
            "      FROM PRODUCT\n" +
            "     WHERE PRODUCT_LIST_PRICE>200\n" +
            ");"
        );

        // Q7
        queries.put("Q7: DEPARTMENTS WITH NO JOB POSTS 1/1–2/1/2011",
            "SELECT D.DEPARTMENT_ID, D.DEPARTMENT_NAME\n" +
            "  FROM DEPARTMENT D\n" +
            "  LEFT JOIN JOB J ON D.DEPARTMENT_ID=J.DEPARTMENT_POST\n" +
            "    AND J.POSTED_DATE BETWEEN '2011-01-01' AND '2011-02-01'\n" +
            " WHERE J.JOB_ID IS NULL;"
        );

        // Q8
        queries.put("Q8: EMPLOYEES WHO APPLIED FOR JOB 12345",
            "SELECT E.EMPLOYEE_ID, CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS EMPLOYEE_NAME, E.DEPARTMENT_ID\n" +
            "  FROM APPLIED AP\n" +
            "  JOIN APPLICANT A ON AP.APPLICANT_ID=A.APPLICANT_ID\n" +
            "  JOIN EMPLOYEE E  ON A.EMPLOYEE_ID=E.EMPLOYEE_ID\n" +
            "  JOIN PERSON P    ON E.EMPLOYEE_ID=P.PERSONAL_ID\n" +
            " WHERE AP.JOB_ID=12345;"
        );

        // Q9
        queries.put("Q9: BEST-SELLING PRODUCT TYPE",
            "SELECT PRODUCT_TYPE\n" +
            "  FROM View3\n" +
            " ORDER BY ITEMS_SOLD DESC\n" +
            " LIMIT 1;"
        );

        // Q10
        queries.put("Q10: PRODUCT TYPE WITH HIGHEST NET PROFIT",
            "SELECT P.PRODUCT_TYPE,\n" +
            "       ROUND(COUNT(S.SALE_ID)*AVG(P.PRODUCT_LIST_PRICE)\n" +
            "       - SUM(IFNULL(V4.TOTAL_PART_COST,0)),2) AS NET_PROFIT\n" +
            "  FROM SALE S\n" +
            "  JOIN PRODUCT P ON S.PRODUCT_ID=P.PRODUCT_ID\n" +
            "  LEFT JOIN View4 V4 ON P.PRODUCT_ID=V4.PRODUCT_ID\n" +
            " GROUP BY P.PRODUCT_TYPE\n" +
            " ORDER BY NET_PROFIT DESC\n" +
            " LIMIT 1;"
        );

        // Q11
        queries.put("Q11: EMPLOYEES WHO HAVE WORKED IN ALL DEPARTMENTS",
            "SELECT E.EMPLOYEE_ID, CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS EMPLOYEE_NAME\n" +
            "  FROM EMPLOYEE E\n" +
            "  JOIN PERSON P ON E.EMPLOYEE_ID=P.PERSONAL_ID\n" +
            "  JOIN EMPLOYEE_WORKS_AT_DEPARTMENT W ON E.EMPLOYEE_ID=W.EMPLOYEE_ID\n" +
            " GROUP BY E.EMPLOYEE_ID\n" +
            "HAVING COUNT(DISTINCT W.DEPARTMENT_ID)=(SELECT COUNT(*) FROM DEPARTMENT);"
        );

        // Q12
        

        // Q13
        queries.put("Q12: SELECTED INTERVIEWEE NAMES & EMAILS",
            "SELECT CONCAT(p.FIRST_NAME,' ',p.LAST_NAME) AS INTERVIEWEE_NAME, ph.PHONE_NO, p.EMAIL\n" +
            "  FROM APPLICANT a\n" +
            "  JOIN PERSON p ON (CASE WHEN a.APPLICANT_CATEGORY='EMPLOYEE' THEN a.EMPLOYEE_ID ELSE a.POTENTIAL_EMPLOYEE_ID END)=p.PERSONAL_ID\n" +
            "  JOIN PERSON_PHONE_NO ph ON ph.PERSONAL_ID=p.PERSONAL_ID\n" +
            " WHERE a.APPLICANT_ID IN (\n" +
            "    SELECT ap.APPLICANT_ID\n" +
            "      FROM APPLIED ap\n" +
            "     GROUP BY ap.APPLICANT_ID\n" +
            "    HAVING COUNT(*)=(\n" +
            "        SELECT COUNT(*) FROM SELECTED_FOR_INTERVIEW sel\n" +
            "         WHERE sel.APPLICANT_ID=ap.APPLICANT_ID\n" +
            "    )\n" +
            ");"
        );

        queries.put("Q13: INTERVIEWEES SELECTED FOR ALL THEIR APPLICATIONS",
            "SELECT DISTINCT CONCAT(P.FIRST_NAME,' ',P.LAST_NAME) AS INTERVIEWEE_NAME, P.EMAIL\n" +
            "  FROM Selected_Interviewees SI\n" +
            "  JOIN SELECTED_FOR_INTERVIEW SEL ON SI.selected_applicant_id=SEL.SELECTED_APPLICANT\n" +
            "  JOIN APPLICANT A ON SEL.APPLICANT_ID=A.APPLICANT_ID\n" +
            "  JOIN PERSON P ON (CASE WHEN A.APPLICANT_CATEGORY='EMPLOYEE' THEN A.EMPLOYEE_ID ELSE A.POTENTIAL_EMPLOYEE_ID END)=P.PERSONAL_ID;"
        );
        // Q14
        queries.put("Q14: HIGHEST AVERAGE MONTHLY SALARY",
            "SELECT EMPLOYEE_ID, EMPLOYEE_NAME, AVG_MONTHLY_SALARY\n" +
            "  FROM View1\n" +
            " ORDER BY AVG_MONTHLY_SALARY DESC\n" +
            " LIMIT 1;"
        );

        // Q15
        queries.put("Q15: VENDOR WITH CHEAPEST ‘CUP’ PART (<4 LB)",
            "SELECT v.VENDOR_ID, v.VENDOR_NAME\n" +
            "  FROM VENDOR v\n" +
            "  JOIN PART_SUPPLIED_BY_VENDOR ps ON v.VENDOR_ID=ps.VENDOR_ID\n" +
            "  JOIN PART p ON ps.PART_ID=p.PART_ID\n" +
            "  JOIN PART_USED_IN_PRODUCT pup ON p.PART_ID=pup.PART_ID\n" +
            "  JOIN PRODUCT pr ON pup.PRODUCT_ID=pr.PRODUCT_ID\n" +
            " WHERE p.PART_TYPE='Cup'\n" +
            "   AND pr.PRODUCT_WEIGHT<4\n" +
            " ORDER BY ps.PART_PRICE\n" +
            " LIMIT 1;"
        );

        queries.put("VIEW1: Avg Monthly Salary by Employee",
            "SELECT * FROM View1");
        queries.put("VIEW2: Rounds Passed / Interviewee & Job",
            "SELECT * FROM View2");
        queries.put("VIEW3: Items Sold by Product Type",
            "SELECT * FROM View3");
        queries.put("VIEW4: Part‐Purchase Cost per Product",
            "SELECT * FROM View4");

        queries.put("Custom SQL…", "");

        for (String label : queries.keySet()) {
            combo.addItem(label);
        }

        combo.addActionListener(e -> {
            boolean custom = "Custom SQL…".equals(combo.getSelectedItem());
            customArea.setEnabled(custom);
            if (!custom) customArea.setText("");
        });

        runBtn.addActionListener(e -> runSelected());

        setVisible(true);
    }

    private void runSelected() {
        String key = (String)combo.getSelectedItem();
        String sql = queries.get(key);
        if (key.equals("Custom SQL…")) {
            sql = customArea.getText().trim();
            if (sql.isEmpty()) {
                JOptionPane.showMessageDialog(this,"Please enter a query.");
                return;
            }
        }
        try (Connection conn = getConnection();
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(sql)) {

            ResultSetMetaData rm = rs.getMetaData();
            int cols = rm.getColumnCount();
            String[] colNames = new String[cols];
            for (int i = 0; i < cols; i++) {
                colNames[i] = rm.getColumnLabel(i+1);
            }
            tableModel.setDataVector(new Object[0][0], colNames);

            while (rs.next()) {
                Object[] row = new Object[cols];
                for (int i = 0; i < cols; i++) {
                    row[i] = rs.getObject(i+1);
                }
                tableModel.addRow(row);
            }

        } catch (SQLException ex) {
            JOptionPane.showMessageDialog(this, "SQL Error:\n" + ex.getMessage());
        }
    }

    private Connection getConnection() throws SQLException {
        String url = "jdbc:mysql://localhost:3306/XYZCOMPANY?serverTimezone=UTC";
        return DriverManager.getConnection(url, "xyzcompany", "projectcode");
    }

    public static void main(String[] args) {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            JOptionPane.showMessageDialog(null,
                "MySQL JDBC driver not found – make sure connector is on classpath");
            System.exit(1);
        }
        SwingUtilities.invokeLater(QueryConsole::new);
    }
}

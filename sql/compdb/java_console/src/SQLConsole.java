// src/SQLConsole.java
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.event.*;
import java.sql.*;
import java.util.*;

public class SQLConsole extends JFrame {
    private JComboBox<String> modeCombo;
    private JComboBox<String> combo;
    private JComboBox<String> dmlTableCombo;
    private JTextArea customArea;
    private JButton runBtn;
    private JTable resultTable;
    private DefaultTableModel tableModel;
    private JPanel dmlFormPanel;

    private List<String> tables = new ArrayList<>();
    private Map<String,List<ColumnMeta>> tableMeta = new HashMap<>();
    private Map<String,String> queries = new LinkedHashMap<>();

    // update staging
    private JTextField pkField;
    private JButton loadBtn;
    private Map<String,JTextField> fieldMap = new LinkedHashMap<>();
    private String currentTable;
    private ColumnMeta currentPk;

    public SQLConsole() {
        super("XYZCOMPANY SQL Console");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(900,700);
        setLayout(new BorderLayout(5,5));

        // top controls
        modeCombo = new JComboBox<>(new String[]{"SELECT","INSERT","UPDATE","DELETE"});
        combo = new JComboBox<>();
        runBtn = new JButton("Run");
        JPanel top = new JPanel(new BorderLayout(5,5));
        top.add(modeCombo, BorderLayout.WEST);
        top.add(combo, BorderLayout.CENTER);
        top.add(runBtn, BorderLayout.EAST);
        add(top, BorderLayout.NORTH);

        // custom SQL area
        customArea = new JTextArea(3,80);
        customArea.setEnabled(false);
        add(new JScrollPane(customArea), BorderLayout.SOUTH);

        // DML form panel
        dmlFormPanel = new JPanel();
        dmlFormPanel.setLayout(new BoxLayout(dmlFormPanel, BoxLayout.Y_AXIS));
        dmlFormPanel.setVisible(false);
        add(new JScrollPane(dmlFormPanel), BorderLayout.EAST);

        // result table
        tableModel = new DefaultTableModel();
        resultTable = new JTable(tableModel);
        add(new JScrollPane(resultTable), BorderLayout.CENTER);

        loadMetadata();
        initQueries();
        setupListeners();

        setVisible(true);
    }

    private void loadMetadata() {
        try (Connection conn = getConnection()) {
            DatabaseMetaData md = conn.getMetaData();
            try (ResultSet rs = md.getTables(null,null,"%",new String[]{"TABLE"})) {
                while(rs.next()) {
                    String tbl = rs.getString("TABLE_NAME");
                    tables.add(tbl);
                    List<ColumnMeta> cols = new ArrayList<>();
                    try (ResultSet cr = md.getColumns(null,null,tbl,"%")) {
                        while(cr.next()) {
                            cols.add(new ColumnMeta(
                                cr.getString("COLUMN_NAME"),
                                cr.getInt("DATA_TYPE"),
                                "YES".equals(cr.getString("IS_AUTOINCREMENT"))
                            ));
                        }
                    }
                    tableMeta.put(tbl,cols);
                    combo.addItem("SELECT * FROM " + tbl);
                }
            }
            dmlTableCombo = new JComboBox<>(tables.toArray(new String[0]));
        } catch(Exception e) {
            JOptionPane.showMessageDialog(this,"Meta error: " + e.getMessage());
        }
    }

    private void initQueries() {
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
        queries.put("VIEW1: Avg Monthly Salary", "SELECT * FROM View1");
        queries.put("VIEW2: Rounds Passed / Interviewee & Job", "SELECT * FROM View2");
        queries.put("VIEW3: Items Sold by Product Type", "SELECT * FROM View3");
        queries.put("VIEW4: Part-Purchase Cost per Product", "SELECT * FROM View4");
        for(String k:queries.keySet()) combo.addItem(k);
        combo.addItem("Custom SQL…");
    }

    private void setupListeners() {
        modeCombo.addActionListener(e-> buildDmlForm());
        combo.addActionListener(e-> buildDmlForm());
        dmlTableCombo.addActionListener(e-> buildDmlForm());
        runBtn.addActionListener(e-> execute());
    }

    private void buildDmlForm() {
        String mode = (String)modeCombo.getSelectedItem();
        boolean isSelect = "SELECT".equals(mode);
        combo.setEnabled(isSelect);
        customArea.setEnabled(isSelect && "Custom SQL…".equals(combo.getSelectedItem()));
        dmlFormPanel.setVisible(!isSelect);
        if(isSelect) return;

        dmlFormPanel.removeAll();
        dmlFormPanel.add(new JLabel("Table:"));
        dmlFormPanel.add(dmlTableCombo);
        currentTable = (String)dmlTableCombo.getSelectedItem();
        List<ColumnMeta> cols = tableMeta.get(currentTable);
        currentPk = cols.stream().filter(c->!c.isAuto).findFirst().orElse(null);

        if("UPDATE".equals(mode)) {
            dmlFormPanel.add(new JLabel("Enter " + currentPk.name + ":"));
            pkField = new JTextField(20);
            dmlFormPanel.add(pkField);
            loadBtn = new JButton("Load Record");
            dmlFormPanel.add(loadBtn);
            loadBtn.addActionListener(ev-> loadRecord());
        } else {
            createFields(cols);
        }
        dmlFormPanel.revalidate();
        dmlFormPanel.repaint();
    }

    private void createFields(List<ColumnMeta> cols) {
        fieldMap.clear();
        for(ColumnMeta c:cols) {
            if(c.isAuto) continue;
            dmlFormPanel.add(new JLabel(c.name));
            JTextField tf = new JTextField(20);
            fieldMap.put(c.name,tf);
            dmlFormPanel.add(tf);
        }
    }

    private void loadRecord() {
        try (Connection conn=getConnection()) {
            String sql = "SELECT * FROM "+currentTable+" WHERE "+currentPk.name+"=?";
            PreparedStatement ps = conn.prepareStatement(sql);
            ps.setString(1,pkField.getText());
            ResultSet rs = ps.executeQuery();
            if(!rs.next()) { JOptionPane.showMessageDialog(this,"No record"); return; }
            dmlFormPanel.removeAll();
            dmlFormPanel.add(new JLabel("Updating " + currentPk.name + "=" + pkField.getText()));
            createFields(tableMeta.get(currentTable));
            for(String col:fieldMap.keySet()) {
                fieldMap.get(col).setText(rs.getString(col));
            }
            dmlFormPanel.revalidate(); dmlFormPanel.repaint();
        } catch(Exception e){ JOptionPane.showMessageDialog(this,e.getMessage()); }
    }

    private void execute() {
        String mode=(String)modeCombo.getSelectedItem();
        if(mode.equals("SELECT")) { runSelect(); return; }
        try (Connection conn=getConnection()) {
            List<String> order = new ArrayList<>(fieldMap.keySet());
            StringBuilder sql=new StringBuilder();
            if(mode.equals("INSERT")) {
                sql.append("INSERT INTO "+currentTable+"(");
                order.forEach(col->sql.append(col).append(",")); sql.setLength(sql.length()-1);
                sql.append(") VALUES ("); for(int i=0;i<order.size();i++) sql.append("?,"); sql.setLength(sql.length()-1); sql.append(")");
            } else if(mode.equals("UPDATE")) {
                sql.append("UPDATE "+currentTable+" SET ");
                order.forEach(col->sql.append(col+"=?,")); sql.setLength(sql.length()-1);
                sql.append(" WHERE "+currentPk.name+"=?");
            } else {
                sql.append("DELETE FROM "+currentTable+" WHERE "+currentPk.name+"=?");
            }
            PreparedStatement ps=conn.prepareStatement(sql.toString());
            int idx=1;
            for(String col:order) ps.setString(idx++,fieldMap.get(col).getText());
            if(!mode.equals("INSERT")) ps.setString(idx,pkField.getText());
            int cnt=ps.executeUpdate();
            JOptionPane.showMessageDialog(this,mode+" OK, rows="+cnt);
        } catch(Exception ex){ JOptionPane.showMessageDialog(this,ex.getMessage()); }
    }

    private void runSelect() {
        String key=(String)combo.getSelectedItem();
        String sql=queries.getOrDefault(key,key);
        if("Custom SQL…".equals(key)) sql=customArea.getText().trim();
        if(sql.isEmpty()) return;
        try(Connection conn=getConnection(); Statement st=conn.createStatement(); ResultSet rs=st.executeQuery(sql)){
            ResultSetMetaData rm=rs.getMetaData();
            int cols=rm.getColumnCount();
            String[] names=new String[cols];
            for(int i=0;i<cols;i++) names[i]=rm.getColumnLabel(i+1);
            tableModel.setDataVector(new Object[0][0],names);
            while(rs.next()){
                Object[] row=new Object[cols]; for(int i=0;i<cols;i++) row[i]=rs.getObject(i+1);
                tableModel.addRow(row);
            }
        } catch(SQLException ex) {
            JOptionPane.showMessageDialog(this,"SQL Error:\n"+ex.getMessage());
        }
    }

    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/XYZCOMPANY?serverTimezone=UTC",
            "xyzcompany","projectcode");
    }

    public static void main(String[] args) throws Exception {
        Class.forName("com.mysql.cj.jdbc.Driver");
        SwingUtilities.invokeLater(SQLConsole::new);
    }

    private static class ColumnMeta { String name; int type; boolean isAuto;
        ColumnMeta(String n,int t,boolean a){name=n;type=t;isAuto=a;}
    }
}

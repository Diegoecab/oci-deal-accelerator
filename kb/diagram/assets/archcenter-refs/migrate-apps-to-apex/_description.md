# Move Oracle Forms applications to Oracle APEX on an Oracle Autonomous Database

- Source: https://docs.oracle.com/en/solutions/migrate-apps-to-apex/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: adb-s, apex
- Tags: application, migration, autonomous

## Summary (catalog)

Oracle Forms to APEX modernization on ADB-S. Automated conversion tools for Forms modules to APEX pages. Manual refinement needed for complex Forms triggers and PL/SQL logic.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows the process of moving on-premises Oracle Forms applications to Oracle APEX applications on Oracle Cloud
 Infrastructure .
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration forms-apps-apex.png 
 forms-apps-apex-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An
 OCI region is a localized geographic area that
 contains one or more data centers, hosting
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A
 VCN is a customizable, software-defined network
 that you set up in an OCI region. Like traditional
 data center networks, VCNs give you control over
 your network environment. A VCN can have multiple
 non-overlapping classless inter-domain routing
 (CIDR) blocks that you can change after you create
 the VCN. You can segment a VCN into subnets, which
 can be scoped to a region or to an availability
 domain. Each subnet consists of a contiguous range
 of addresses that don't overlap with the other
 subnets in the VCN. You can change the size of a
 subnet after creation. A subnet can be public or
 private. 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that is allowed in and out of the subnet.

 
 
- Autonomous Transaction
 Processing 
 Oracle Autonomous Transaction
 Processing is a self-driving, self-securing,
 self-repairing database service that is optimized
 for transaction processing workloads. You do not
 need to configure or manage any hardware, or
 install any software. OCI handles creating,
 backing up, patching, upgrading, and tuning the
 database.
 

 
 
- Identity and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for OCI and
 Oracle Cloud Applications. The IAM API and the
 user interface enable you to manage identity
 domains and the resources within them. Each OCI
 IAM identity domain represents a standalone
 identity and access management solution or a
 different user population.
 

 
 
- Audit 
The
 Oracle Cloud Infrastructure Audit service automatically records calls to all
 supported OCI public application programming
 interface (API) endpoints as log events. All OCI
 services support logging by Oracle Cloud Infrastructure Audit .
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point
 to plan modernizing to Oracle APEX . Your requirements might differ from the architecture described here. 
 

 
 
- VCN 
When you create a VCN, determine how many IP addresses your
 cloud resources in each subnet require. Using Classless Inter-Domain Routing
 (CIDR) notation, specify a subnet mask and a network address range large enough
 for the required IP addresses. Use CIDR blocks that are within the standard
 private IP address space.

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
 
- 
 
 
When you design the subnets, consider functionality and security requirements.
 All compute instances within the same tier or role should go into the same
 subnet.

 
 
Use regional subnets.

 
 
 
- Security lists 
Use security lists to define ingress and egress rules that apply to the entire subnet.

 
 
- Cloud Guard 
Clone and customize the default recipes provided by Oracle to create custom detector and responder recipes. These recipes enable you to specify what type of security violations generate a warning and what actions are allowed to be performed on them. For example, you might want to detect OCI Object Storage buckets that have visibility set to public. 
 

 
Apply Oracle Cloud Guard at the tenancy level to cover the broadest scope and to reduce the administrative burden of maintaining multiple configurations.
 

 
You can also use the Managed List feature to apply certain configurations to detectors.

 
 
- Security Zones 
For resources that require maximum security, Oracle recommends that you use security zones. A security zone is a compartment associated with an Oracle-defined recipe of security policies that are based on best practices. For example, the resources in a security zone must not be accessible from the public internet and they must be encrypted using customer-managed keys. When you create and update resources in a security zone, OCI validates the operations against the policies in the recipe, and prevents operations that violate any of the policies.

 
 
- Schema 
Retain the database structure that Oracle
 Forms was built on, as is, and use that as the schema for Oracle APEX .
 

 
 
- Business Logic 
Most of the business logic for
 Oracle Forms is in triggers, program units, and events. Before starting the
 migration of Oracle Forms to Oracle APEX , migrate the business logic to stored procedures, functions, and packages in
 the database. 
 

 
 
 

 

 
 
Considerations

 

 

 Consider the following key items when moving Oracle Forms Object
 navigator components to Oracle APEX : 
 
 

 
 
- Data Blocks 
A data block from Oracle Forms relates to Oracle APEX with each page broken up into several regions and
 components. Review the Oracle APEX Component Templates available in the Universal
 Theme.
 

 
 
- Triggers 
In Oracle Forms, triggers control almost everything.
 In Oracle APEX , control is based on flexible conditions that are
 activated when a page is submitted and are managed by
 validations, computations, dynamic actions, and
 processes.
 

 
 
- Alerts 
Most messages in Oracle APEX are generated when you submit a page.
 

 
 
- Attached Libraries 
 Oracle APEX takes care of the JavaScript and CSS libraries that
 support the Universal Theme, which supports all of the
 components that you need for flexible, dynamic applications.
 You can include your own JavaScript and CSS in several ways,
 mostly through page attributes. You can choose to add inline
 code as reference files that exist either in the database as
 a BLOB ( #APP_IMAGES# ) or sit on the middle
 tier, typically served by Oracle REST Data Services (ORDS).
 When a reference file is on an Oracle WebLogic Server, the
 file location is prefixed with
 #IMAGE_PREFIX# .
 

 
 
- Editors 
 Oracle APEX has a text area and a rich text editor, which is
 equivalent to Editors in Oracle Forms. 
 

 
 
- List of Values (LOV) 
In Oracle APEX , the LOV is coupled with the Item type. A radio group
 works well with a small handful of values. Select Lists for
 middle-sized sets, and select Popup LOV for large data sets.
 You can use the queries from Record Group in Oracle Forms
 for the LOV query in Oracle APEX . LOV's in Oracle APEX can be dynamically driven by a SQL query, or be
 statically defined. A static definition allows a variety of
 conditions to be applied to each entry. These LOVs can then
 be associated with Items such as Radio Groups and Select
 Lists, or with a column in a report, to translate a code to
 a label.
 

 
 
- Parameters 
Page Items in Oracle APEX are populated between pages to pass information to the
 next page, such as the selected record in a report. Larger
 forms with a number of items are generally submitted as a
 whole, where the page process handles t

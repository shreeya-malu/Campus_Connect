-- Table 1: Users
CREATE TABLE IF NOT EXISTS Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    passing_date DATE,
    branch VARCHAR(100),
    role ENUM('student', 'teaching faculty', 'admin'),
    is_active TINYINT(1) NOT NULL
);

-- Table 2: Resources
CREATE TABLE IF NOT EXISTS Resources (
    Resource_id INT PRIMARY KEY AUTO_INCREMENT,
    Contributor_id INT NOT NULL,
    Domain_id INT NOT NULL,
    ResourceType_id INT NOT NULL,
    Link VARCHAR(255),
    FOREIGN KEY (Contributor_id) REFERENCES Contributors(Contributor_id),
    FOREIGN KEY (Domain_id) REFERENCES Domains(Domain_id),
    FOREIGN KEY (ResourceType_id) REFERENCES ResourceTypes(ResourceType_id)
);

-- Table 3: Contributors
CREATE TABLE IF NOT EXISTS Contributors (
    Contributor_id INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Year INT
);

-- Table 4: Domains
CREATE TABLE IF NOT EXISTS Domains (
    Domain_id INT PRIMARY KEY AUTO_INCREMENT,
    Domain_name VARCHAR(100) NOT NULL
);

-- Table 5: ResourceTypes
CREATE TABLE IF NOT EXISTS ResourceTypes (
    ResourceType_id INT PRIMARY KEY AUTO_INCREMENT,
    ResourceType_name VARCHAR(100) NOT NULL
);

-- Table 6: Opportunities
CREATE TABLE IF NOT EXISTS Opportunities (
    opp_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    link VARCHAR(255),
    posted_by INT NOT NULL,
    FOREIGN KEY (posted_by) REFERENCES Users(id)
);

-- Table 7: OpportunityTypes
CREATE TABLE IF NOT EXISTS OpportunityTypes (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) NOT NULL
);

-- Table 8: Collaborations
CREATE TABLE IF NOT EXISTS Collaborations (
    collaboration_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    collaboration_type VARCHAR(100),
    posted_by INT NOT NULL,
    contact_link VARCHAR(255),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (posted_by) REFERENCES Users(id)
);

-- Table 9: Collaborators
CREATE TABLE IF NOT EXISTS Collaborators (
    collaborator_id INT PRIMARY KEY AUTO_INCREMENT,
    collaboration_id INT NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100) NOT NULL,
    student_linkedin VARCHAR(100),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (collaboration_id) REFERENCES Collaborations(collaboration_id)
);

-- Table 10: News
CREATE TABLE IF NOT EXISTS News (
    news_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    category VARCHAR(50),
    created_at DATETIME NOT NULL
);

-- Table 11: NewsRequests
CREATE TABLE IF NOT EXISTS NewsRequests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    category VARCHAR(50),
    requested_by INT NOT NULL,
    status ENUM('pending', 'approved', 'rejected'),
    submitted_at DATETIME NOT NULL,
    FOREIGN KEY (requested_by) REFERENCES Users(id)
);

-- Table 12: DomainRequests
CREATE TABLE IF NOT EXISTS DomainRequests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    domain_name VARCHAR(100) NOT NULL,
    requested_by INT NOT NULL,
    request_date DATETIME NOT NULL,
    status ENUM('pending', 'approved', 'rejected'),
    FOREIGN KEY (requested_by) REFERENCES Users(id)
);

-- Table 13: CarouselItem
CREATE TABLE IF NOT EXISTS CarouselItem (
    id INT PRIMARY KEY AUTO_INCREMENT,
    image_url VARCHAR(255) NOT NULL,
    link VARCHAR(255),
    title VARCHAR(100),
    description TEXT
);

-- Table 14: Events
CREATE TABLE IF NOT EXISTS Events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_name VARCHAR(100) NOT NULL,
    building_id INT,
    FOREIGN KEY (building_id) REFERENCES Buildings(id)
);

-- Table 15: Buildings
CREATE TABLE IF NOT EXISTS Buildings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL
);

-- Table 16: Activity log
CREATE TABLE IF NOT EXISTS Activity_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action_table ENUM('news', 'opportunities', 'collaborations', 'others'),
    target_table VARCHAR(100) NOT NULL,
    target_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Table 17: Alumnae
CREATE TABLE IF NOT EXISTS Alumnae (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    branch VARCHAR(100),
    role VARCHAR(20),
    passing_date DATE,
    Deactivated_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

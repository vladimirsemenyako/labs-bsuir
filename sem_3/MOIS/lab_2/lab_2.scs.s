section_subject_domain_of_legislative_acts = [*
        subject_domain_of_legislative_acts => nrel_main_idtf:[Предметная область законодательных актов] (*<- lang_ru;;*);[Subject domain of legislative acts](*<- lang_en;;*);
                               <- sc_node_struct;
                               -> rrel_explored_relation: nrel_lawmaking_process;
                                                        nrel_legal_interpretation;
                                                        nrel_enforcement_practices;
                                                        nrel_judicial_decision;
                                                        nrel_public_discussion; 
                                                        nrel_law_revision; 
                                                        nrel_legal_analysis;

                               => nrel_private_subject_domain: subject_domain_of_lawmaking;
                                                               subject_domain_of_interpretation; 
                                                               subject_domain_of_enforcement; 
                                                               subject_domain_of_judicial_system; 
                                                               subject_domain_of_public_opinion; 
                                                               subject_domain_of_revision;                      
                               <- subject_domain;
                               -> rrel_maximum_studied_object_class: concept_laws_and_regulations; 
                               -> rrel_not_maximum_studied_object_class: concept_constitutional_law; 
                                                                         concept_civil_law;                
                                                                         concept_criminal_law ;;                          
*];;



section_subject_domain_of_legislative_acts  => nrel_main_idtf:[Раздел. Предметная область законодательных актов] (*<- lang_ru;;*);[Section. Subject domain of legislative acts](*<- lang_en;;*);
                                <= nrel_section_decomposition: ...
                                                            (* <-sc_node_tuple;; 
                                                               -> section_subject_domain_of_lawmaking;;
                                                               -> section_subject_domain_of_interpretation;;
                                                               -> section_subject_domain_of_enforcement;;
                                                               -> section_subject_domain_of_judicial_system;;
                                                               -> section_subject_domain_of_public_opinion;;
                                                               -> section_subject_domain_of_revision;;
                                                             *);
                                -> rrel_key_sc_element: nrel_lawmaking_process; 
                                                        nrel_legal_interpretation;
                                                        nrel_enforcement_practices;
                                                        nrel_judicial_decision;
                                                        nrel_public_discussion; 
                                                        nrel_law_revision; 
                                                        nrel_legal_analysis;
							concept_laws_and_regulations; 
							concept_constitutional_law; 
							concept_civil_law;                
                                                        concept_criminal_law;
                                <- non_atomic_section;;
  
  
                                
                                   
nrel_lawmaking_process  <- sc_node_norole_relation; 
                               => nrel_main_idtf:[законодательный процесс*] (*<- lang_ru;;*);[lawmaking process](*<- lang_en;;*);;
                               
nrel_legal_interpretation <- sc_node_norole_relation; 
              => nrel_main_idtf:[правовая интерпретация*] (*<- lang_ru;;*);[legal interpretation*](*<- lang_en;;*);;
                               
nrel_enforcement_practices <- sc_node_norole_relation; 
              => nrel_main_idtf:[правоприменительная практика*] (*<- lang_ru;;*);[enforcement practices*](*<- lang_en;;*);;
                               
nrel_judicial_decision <- sc_node_norole_relation; 
          => nrel_main_idtf:[судебные решения*] (*<- lang_ru;;*);[judicial decisions*](*<- lang_en;;*);;
 
nrel_public_discussion <- sc_node_norole_relation; 
                 => nrel_main_idtf:[общественное обсуждение*] (*<- lang_ru;;*);[public discussion*](*<- lang_en;;*);;
                               
nrel_law_revision <- sc_node_norole_relation; 
                     => nrel_main_idtf:[пересмотр законодательства*] (*<- lang_ru;;*);[law revision*](*<- lang_en;;*);;

nrel_legal_analysis <- sc_node_norole_relation; 
                     => nrel_main_idtf:[правовой анализ*] (*<- lang_ru;;*);[legal analysis*](*<- lang_en;;*);;                               




section_subject_domain_of_lawmaking => nrel_main_idtf:[Раздел. Предметная область законодательного процесса] (*<- lang_ru;;*);[Section. Subject domain of lawmaking](*<- lang_en;;*); 
                                       <- sc_node_struct;;

section_subject_domain_of_interpretation => nrel_main_idtf:[Раздел. Предметная область правовой интерпретации] (*<- lang_ru;;*);[Section. Subject domain of legal interpretation](*<- lang_en;;*);   
                                       <- sc_node_struct;;

section_subject_domain_of_enforcement => nrel_main_idtf:[Раздел. Предметная область правоприменительной практики] (*<- lang_ru;;*);[Section. Subject domain of enforcement practices](*<- lang_en;;*);
                                   <- sc_node_struct;;

section_subject_domain_of_judicial_system => nrel_main_idtf:[Раздел. Предметная область судебной системы] (*<- lang_ru;;*);[Section. Subject domain of judicial system](*<- lang_en;;*);
                                           <- sc_node_struct;;

section_subject_domain_of_public_opinion => nrel_main_idtf:[Раздел. Предметная область общественного мнения] (*<- lang_ru;;*);[Section. Subject domain of public opinion ](*<- lang_en;;*);
                                           <- sc_node_struct;;
    
section_subject_domain_of_revision => nrel_main_idtf:[Раздел. Предметная область пересмотра законодательства] (*<- lang_ru;;*);[Section. Subject domain of law revision](*<- lang_en;;*);
                                       <- sc_node_struct;;
                                                     
                                                     
  
                                                     
subject_domain_of_lawmaking => nrel_main_idtf:[Предметная область законодательного процесса] (*<- lang_ru;;*);[Subject domain of lawmaking](*<- lang_en;;*);
                        <- sc_node_struct;;
                               
subject_domain_of_interpretation => nrel_main_idtf:[Предметная область правовой интерпретации] (*<- lang_ru;;*);[Subject domain of legal interpretation](*<- lang_en;;*);
                        <- sc_node_struct;;
                               
subject_domain_of_enforcement => nrel_main_idtf:[Предметная область правоприменительной практики] (*<- lang_ru;;*);[Subject domain of enforcement practices](*<- lang_en;;*);
                           <- sc_node_struct;; 
                               
subject_domain_of_judicial_system => nrel_main_idtf:[Предметная область судебной системы] (*<- lang_ru;;*);[Subject domain of judicial system](*<- lang_en;;*);
                               <- sc_node_struct;;  

subject_domain_of_public_opinion => nrel_main_idtf:[Предметная область общественного мнения] (*<- lang_ru;;*);[Subject domain of public opinion](*<- lang_en;;*);
                               <- sc_node_struct;;   

subject_domain_of_revision => nrel_main_idtf:[Предметная область пересмотра законодательства] (*<- lang_ru;;*);[Subject domain of law revision](*<- lang_en;;*);
                               <- sc_node_struct;;                                
                                                              


concept_legislative_acts <- sc_node_class;
                => nrel_main_idtf:[законодательные акты] (*<- lang_ru;;*);[legislative acts](*<- lang_en;;*);;  
                
concept_constitutional_law <- sc_node_class;
                 => nrel_main_idtf:[конституционное право] (*<- lang_ru;;*);[constitutional law](*<- lang_en;;*);; 
                
concept_civil_law<- sc_node_class;
                => nrel_main_idtf:[гражданское право] (*<- lang_ru;;*);[civil law](*<- lang_en;;*);; 
                
concept_criminal_law<- sc_node_class;
              => nrel_main_idtf:[уголовное право] (*<- lang_ru;;*);[criminal law](*<- lang_en;;*);;  
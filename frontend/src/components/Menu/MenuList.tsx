import React from 'react';
import { 
  Grid, 
  Card, 
  CardContent, 
  Typography,
  CardMedia,
  IconButton,
  Box 
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { MenuItem } from '../../types';

interface Props {
  items: MenuItem[];
  onEdit: (item: MenuItem) => void;
  onDelete: (uuid: string) => void;
}

export const MenuList: React.FC<Props> = ({ items, onEdit, onDelete }) => {
  return (
    <Grid container spacing={2}>
      {items.map((item) => (
        <Grid item xs={12} sm={6} md={4} key={item.uuid}>
          <Card>
            {item.image_url && (
              <CardMedia
                component="img"
                height="140"
                image={item.image_url}
                alt={item.name}
              />
            )}
            <CardContent>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">{item.name}</Typography>
                <Typography variant="h6" color="primary">
                  ${item.price}
                </Typography>
              </Box>
              <Typography color="textSecondary">{item.description}</Typography>
              <Box display="flex" justifyContent="flex-end" mt={1}>
                <IconButton onClick={() => onEdit(item)}>
                  <Edit />
                </IconButton>
                <IconButton onClick={() => onDelete(item.uuid)}>
                  <Delete />
                </IconButton>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
